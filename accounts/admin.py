from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_customer', 'is_vendor', 'is_vendor_approved', 'is_staff')
    list_filter = ('is_vendor', 'is_vendor_approved')
    list_editable = ('is_vendor_approved',) # Superuser yahi se direct approve kar dega
    search_fields = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)