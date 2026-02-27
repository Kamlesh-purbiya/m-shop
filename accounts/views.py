from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q
from django.contrib import messages
from store.models import Product, OrderItem, Order
from store.forms import ProductForm
from django.utils.text import slugify
import uuid

User = get_user_model()

def register(request):
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account and are logged in.')
        return redirect('store')

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Checkbox ki value pakdna (Agar tick kiya hoga to 'on' aayega)
        is_seller = request.POST.get('is_seller') == 'on'

        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
                return redirect('register')
            else:
                try:
                    user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
                except TypeError:
                    user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
                
                # Agar seller hai toh is_vendor True kar do
                if is_seller:
                    user.is_vendor = True
                    # Optional: user.is_staff = True (Agar unko default Django admin panel bhi dena ho to)
                user.save()

                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('store')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = authenticate(request, email=email, password=password)
            if user is None:
                user = authenticate(request, username=email, password=password)
        except Exception:
            user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            # LOGIC: Agar vendor hai toh Seller Dashboard bhejo, warna Normal Store
            if getattr(user, 'is_vendor', False):
                return redirect('vendor_dashboard')
            return redirect('store')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
            
    return render(request, 'accounts/login.html')

# --- NAYA VIEW: SELLER CUSTOM DASHBOARD ---
def vendor_dashboard(request):
    # Sirf login users aur jo vendor hain wahi is page par aa sakte hain
    if not request.user.is_authenticated or not getattr(request.user, 'is_vendor', False):
        messages.error(request, 'You do not have permission to view the Seller Dashboard.')
        return redirect('store')

    # Vendor ke khud ke add kiye hue products aur unke orders nikalna
    my_products = Product.objects.filter(vendor=request.user)
    my_orders = OrderItem.objects.filter(product__vendor=request.user).order_by('-id')

    context = {
        'products': my_products,
        'orders': my_orders,
    }
    return render(request, 'accounts/vendor_dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')


def add_product(request):
    # Security check: Sirf login aur vendor hi is page par aa sakte hain
    if not request.user.is_authenticated or not getattr(request.user, 'is_vendor', False):
        messages.error(request, 'Permission Denied! Only sellers can add products.')
        return redirect('store')

    if request.method == 'POST':
        # Image upload ke liye request.FILES zaroori hai
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user # Logged in seller ko assign kar diya
            
            # Auto-generate unique slug (URL) bina error ke
            base_slug = slugify(product.product_name)
            unique_id = str(uuid.uuid4())[:6] 
            product.slug = f"{base_slug}-{unique_id}"
            
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('vendor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()

    return render(request, 'accounts/add_product.html', {'form': form})


# --- EDIT PRODUCT VIEW ---
def edit_product(request, pk):
    # Sirf login vendors allowed hain
    if not request.user.is_authenticated or not getattr(request.user, 'is_vendor', False):
        messages.error(request, 'Permission Denied!')
        return redirect('store')

    # Ensure karein ki ye product is hi vendor ka hai
    product = get_object_or_404(Product, id=pk, vendor=request.user)

    if request.method == 'POST':
        # instance=product lagane se form me purana data pre-fill ho jata hai aur naya create hone ki jagah update hota hai
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'accounts/edit_product.html', {'form': form, 'product': product})


# --- DELETE PRODUCT VIEW ---
def delete_product(request, pk):
    # Sirf login vendors allowed hain
    if not request.user.is_authenticated or not getattr(request.user, 'is_vendor', False):
        messages.error(request, 'Permission Denied!')
        return redirect('store')

    # Product fetch karo
    product = get_object_or_404(Product, id=pk, vendor=request.user)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('vendor_dashboard')

    return render(request, 'accounts/delete_product.html', {'product': product})


# --- CUSTOMER DASHBOARD VIEW ---
def customer_dashboard(request):
    # Agar user login nahi hai toh login page par bhejo
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view your dashboard.')
        return redirect('login')

    # Agar galti se koi Seller is page par aa jaye, toh usko uske dashboard par bhej do
    if getattr(request.user, 'is_vendor', False):
        return redirect('vendor_dashboard')

    # FIX: Sirf 'email' se filter karenge kyunki aapke model me email field hi available hai
    my_orders = Order.objects.filter(email=request.user.email).order_by('-created_at')

    context = {
        'orders': my_orders,
    }
    return render(request, 'accounts/customer_dashboard.html', context)