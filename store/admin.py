from django.contrib import admin
from .models import Category, Product, ProductGallery, Order, OrderItem

# Category Admin (Sirf Superuser add kar sakega)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

# Product Gallery Inline
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

# Product Admin (Vendor sirf apne product dekhega)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_active')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

    # Vendor ko field hide karne ke liye
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Agar vendor hai toh use Vendor select karne ka option mat do, automatic save hoga
            if 'vendor' in form.base_fields:
                form.base_fields['vendor'].disabled = True
        return form

    # List mein sirf apne products dikhane ke liye
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(vendor=request.user) # Vendor ko sirf apne products dikhenge

    # Save karte waqt automatic logged-in user ko vendor set karna
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.vendor = request.user
        super().save_model(request, obj, form, change)


# Order Item Admin (Vendor ke orders yahan dikhenge)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_order_id', 'get_customer_name', 'quantity', 'price')
    list_filter = ('product',)
    
    # Custom columns dikhane ke liye
    def get_order_id(self, obj):
        return obj.order.id
    get_order_id.short_description = 'Order ID'

    def get_customer_name(self, obj):
        return obj.order.full_name
    get_customer_name.short_description = 'Customer Name'

    # Vendor ko sirf unke products ke order items dikhane ke liye
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(product__vendor=request.user)

    # Vendor inko delete ya change nahi kar sakta, sirf dekh sakta hai
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Main Order Admin (Sirf Superuser poori details dekh payega)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'city', 'total_paid', 'created_at')
    list_filter = ('created_at', 'city')
    search_fields = ('full_name', 'email')
    inlines = [OrderItemInline]
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Sabko Register Karein
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin) # Vendor apne order items yahan dekhega