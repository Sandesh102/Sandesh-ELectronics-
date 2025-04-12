from django import forms
from .models import Order, Review

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'phone_number']

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        required=False
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
