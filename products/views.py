from products.models import Category, Product,CartItem, Order, UserProfile, OrderItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings
import qrcode
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Count
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
@login_required(login_url='login')
def homepage(request):
    # Featured Products (most reviewed)
    featured_products = Product.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:4]
    
    # New Arrivals
    new_arrivals = Product.objects.order_by('-created_at')[:4]
    
    # Popular Categories
    popular_categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:6]
    
    # Recommendations for logged-in users
    recommended_products = []
    if request.user.is_authenticated:
        try:
            # Get user's purchase history
            user_orders = Order.objects.filter(
                user=request.user,
                status='Delivered'
            )
            
            if user_orders.exists():
                # Get categories from user's orders
                user_categories = OrderItem.objects.filter(
                    order__in=user_orders
                ).values_list('product__category', flat=True).distinct()
                
                # Recommend products from similar categories
                recommended_products = Product.objects.filter(
                    category__in=user_categories
                ).exclude(
                    orderitem__order__user=request.user
                ).order_by('?')[:4]
            else:
                # If no order history, show popular products
                recommended_products = Product.objects.annotate(
                    review_count=Count('reviews')
                ).order_by('-review_count')[:4]
        except:
            # Fallback to popular products if there's any error
            recommended_products = Product.objects.annotate(
                review_count=Count('reviews')
            ).order_by('-review_count')[:4]
    
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'popular_categories': popular_categories,
        'recommended_products': recommended_products,
    }
    return render(request, 'products/home.html', context)
def products(request):
    return render(request, 'products/products.html')
@login_required(login_url='login')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'products/cart.html', context)

def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all().order_by('-created_at')
    user_review = None
    can_review = False
    
    if request.user.is_authenticated:
        # Check if user has a delivered order containing this product
        delivered_orders = Order.objects.filter(
            user=request.user,
            status='Delivered'
        )
        has_delivered_order = any(
            product in order.orderitem_set.values_list('product', flat=True) 
            for order in delivered_orders
        )
        user_review = reviews.filter(user=request.user).first()
        can_review = has_delivered_order and not user_review
    
    if request.method == 'POST' and request.user.is_authenticated:
        # Recheck delivery status when submitting review
        if not can_review and not user_review:
            messages.error(request, "You can only review products that you have purchased and received.")
            return redirect('product_detail', slug=slug)
            
        if user_review:
            form = ReviewForm(request.POST, instance=user_review)
        else:
            form = ReviewForm(request.POST)
            
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('product_detail', slug=slug)
    else:
        form = ReviewForm(instance=user_review) if user_review else ReviewForm()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
    
    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
        'avg_rating': avg_rating,
        'can_review': can_review
    }
    return render(request, 'products/detail.html', context)

    
def category(request):
    categories = Category.objects.all()  # Get all categories

    # Filter products based on category and price range
    products = Product.objects.all()

    # Filter by category if selected
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Filter by min price if provided
    min_price = request.GET.get('min_price')
    if min_price:
        products = products.filter(price__gte=min_price)

    # Filter by max price if provided
    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(price__lte=max_price)

    # Pass the filtered products and categories to the template
    return render(request, 'products/category.html', {
        'categories': categories,
        'products': products
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get the quantity from the POST request and set a default of 1 if not provided
    quantity = request.POST.get('quantity')
    
    if not quantity or int(quantity) <= 0:
        quantity = 1  # Default to 1 if quantity is invalid or missing

    # Ensure quantity is treated as an integer
    quantity = int(quantity)

    # Retrieve the cart item or create a new one
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        # If the cart item already exists, update the quantity
        cart_item.quantity += quantity
        cart_item.save()
    else:
        # If the cart item is new, set the quantity
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart')  # Redirect to the cart page



from django.core.files.storage import FileSystemStorage

@login_required(login_url='login')
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    qr_code_path = f"{settings.MEDIA_URL}qr_codes/order_payment_qr.png"  # Update this to your static QR path

    if request.method == "POST":
        form = DeliveryForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            order.payment_proof = request.FILES.get('payment_proof')  # Save the uploaded file
            order.save()

            # Clear the cart after checkout
            cart_items.delete()

            return render(request, 'products/checkout_success.html', {'order': order, 'qr_code_path': qr_code_path})
    else:
        form = DeliveryForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'qr_code_path': qr_code_path,
    }
    return render(request, 'products/checkout.html', context)



@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')

def cart(request):
    # Get the cart items for the logged-in user
    cart_items = CartItem.objects.filter(user=request.user)

    # Calculate the total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'products/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == "POST":
        action = request.POST.get('action')
        if action == "increase":
            item.quantity += 1
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1
        item.save()
    return redirect('cart')  # Redirect back to the cart page

@login_required(login_url='login')
def checkout_success(request, order_id):
    try:
        # Retrieve the completed order
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        # Redirect to the cart or an error page if the order does not exist
        messages.error(request, "Order not found.")
        return redirect('cart')  # Replace 'cart' with the appropriate URL name

    context = {
        'order': order,
        'qr_code_path': f"{settings.MEDIA_URL}qr_codes/order_{order.id}.png",  # Update to your QR code path
    }
    return render(request, 'products/checkout_success.html', context)

@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'reviews': reviews,
        'user': user
    }
    return render(request, 'users/profile.html', context)

@csrf_exempt
def verify_khalti(request):
    if request.method == "POST":
        token = request.POST.get("token")
        amount = request.POST.get("amount")
        
        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
        }
        
        response = requests.post(url, payload, headers=headers)
        
        if response.status_code == 200:
            # Payment successful
            # Create order and clear cart
            order = Order.objects.create(
                user=request.user,
                total_price=float(amount) / 100,  # Convert paisa to rupees
                payment_method="Khalti",
                status="Processing"
            )
            
            # Clear cart
            CartItem.objects.filter(user=request.user).delete()
            
            return JsonResponse({
                "success": True,
                "order_id": order.id
            })
        
        return JsonResponse({
            "success": False,
            "error": "Payment verification failed"
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
