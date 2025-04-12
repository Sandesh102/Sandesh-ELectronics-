from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from products.models import UserProfile, Order, Review
from django.views.decorators.http import require_http_methods

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Create or update user profile
            profile = UserProfile.objects.get_or_create(user=user)[0]
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
                profile.save()
            
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # Redirect to next page if specified, otherwise to homepage
            next_page = request.GET.get('next')
            return redirect(next_page if next_page else 'homepage')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'users/login.html')

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('homepage')

@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    
    if request.method == 'POST':
        # Handle profile update
        profile = user.userprofile
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'orders': orders,
        'reviews': reviews
    }
    return render(request, 'users/profile.html', context)
