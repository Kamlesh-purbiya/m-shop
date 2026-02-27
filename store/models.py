from django.db import models
from django.conf import settings # CustomUser ko link karne ke liye

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    category_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name

class Product(models.Model):
    # Relational Fields
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # Vendor wahi hoga jiska is_vendor=True ho
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_vendor': True})
    
    # Product Details
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='photos/products') # Main Image
    
    # Inventory Management
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True) # Superuser ise ban kar sakta hai
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # Dynamic Out of Stock Logic
    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.product_name

# Ek product ki multiple images ke liye (Gallery)
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE, related_name='product_gallery')
    image = models.ImageField(upload_to='photos/products/gallery', max_length=255)

    def __str__(self):
        return f"Gallery image for {self.product.product_name}"
    


# store/models.py ke sabse niche ye add karein

class Order(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"