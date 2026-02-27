from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Hum vendor aur slug ko form me nahi dikhayenge, wo background me auto-save honge
        fields = ['product_name', 'category', 'price', 'stock', 'description', 'images']
        
        # Form ko thoda sundar (Bootstrap classes) banane ke liye widgets ka use karenge
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total items available'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your product...'}),
            'images': forms.FileInput(attrs={'class': 'form-control'}),
        }