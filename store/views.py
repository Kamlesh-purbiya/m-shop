from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, Category, ProductGallery
from django.db.models import Q
from django.template.loader import render_to_string
from django.shortcuts import redirect
from .models import Order, OrderItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from cart.cart import Cart

def store_home(request, category_slug=None):
    categories = None
    products = None
    
    query = request.GET.get('q', '') 

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_active=True).order_by('-created_date')
    elif query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) | 
            Q(category__category_name__icontains=query),
            is_active=True
        ).order_by('-created_date')
    else:
        products = Product.objects.filter(is_active=True).order_by('-created_date')

    # --- PAGINATION LOGIC ---
    # 1. Page par kitne products dikhane hain
    paginator = Paginator(products, 4) 
    page = request.GET.get('page')
    # 3. Us page ke products nikalein
    paged_products = paginator.get_page(page)
    
    product_count = products.count()
    all_categories = Category.objects.all()

    context = {
        'products': paged_products, # <--- 'products' ki jagah 'paged_products' bhejein
        'all_categories': all_categories,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def search_products_ajax(request):
    query = request.GET.get('q', '')
    
    # Agar query hai toh naam ya category ke basis par filter karo
    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) | 
            Q(category__category_name__icontains=query),
            is_active=True
        ).order_by('-created_date')
    else:
        products = Product.objects.filter(is_active=True).order_by('-created_date')
    
    # Render_to_string HTML generate karke JSON format me return karega
    context = {'products': products}
    html_data = render_to_string('store/ajax_product_list.html', context, request=request)
    
    return JsonResponse({'data': html_data, 'count': products.count()})


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        
        # NAYA LOGIC: Related Products fetch karna
        # 1. Usi category ke products lo
        # 2. .exclude(id=single_product.id) se current product ko hata do
        # 3. .order_by('?') se random products dikhao (ya latest ke liye '-id')
        # 4. [:4] se limit kardo ki sirf 4 products dikhe
        related_products = Product.objects.filter(category=single_product.category).exclude(id=single_product.id).order_by('?')[:4]
        
    except Exception as e:
        raise e
    
    # Is product ki saari extra gallery images fetch karna
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = {
        'single_product': single_product,
        'related_products': related_products,
        'product_gallery' : product_gallery
    }
    return render(request, 'store/product_detail.html', context)


def checkout(request):
    cart = Cart(request)
    # Agar cart khali hai to checkout par mat jane do
    if len(cart) == 0:
        return redirect('store')
    return render(request, 'store/checkout.html', {'cart': cart})

def place_order(request):
    cart = Cart(request)
    if request.method == 'POST':
        # Form se data nikalna
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        
        # 1. Main Order save karna
        order = Order.objects.create(
            full_name=full_name, email=email, phone=phone, 
            address=address, city=city, state=state, 
            zipcode=zipcode, total_paid=cart.get_total_price()
        )
        
        # 2. Cart ke saare items ko OrderItem mein save karna
        for item in cart:
            OrderItem.objects.create(
                order=order, 
                product=item['product'], 
                price=item['price'], 
                quantity=item['qty']
            )
            
            # (Optional) Stock kam karna
            product = item['product']
            if product.stock >= item['qty']:
                product.stock -= item['qty']
                if product.stock == 0:
                    product.in_stock = False
                product.save()
        
        # 3. Order save hone ke baad Cart ko khali (Clear) kar dena
        cart.cart.clear()
        request.session.modified = True
        
        # Success page par bhej dena
        return render(request, 'store/order_success.html')
        
    return redirect('checkout')

# store/urls.py ke urlpatterns list mein inhe add karein


# --- SEARCH PRODUCTS VIEW ---
def search(request):
    # URL mein se 'q' (query) nikalna jo user ne type kiya hai
    query = request.GET.get('q')
    products = None
    product_count = 0
    
    if query:
        # Q object ka use: Ya toh product ke naam mein search karo, YA uske description mein
        products = Product.objects.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query)
        ).order_by('-id')
        
        product_count = products.count()
        
    context = {
        'products': products,
        'query': query,
        'product_count': product_count,
    }
    return render(request, 'store/search.html', context)
