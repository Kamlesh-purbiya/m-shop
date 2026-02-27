from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from store.models import Product
from .cart import Cart

# Cart dikhane ka view
def cart_summary(request):
    cart = Cart(request)
    return render(request, 'cart/cart_summary.html', {'cart': cart})

# Cart me item add karne ka view (Ye aapke paas pehle se hai)
def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty', 1))
        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, quantity=product_qty)
        cart_quantity = cart.__len__()
        return JsonResponse({'qty': cart_quantity})

# Quantity Update karne ka view
def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product=product_id, quantity=product_qty)
        
        response = JsonResponse({'qty': cart.__len__(), 'total': cart.get_total_price()})
        return response

# Item Delete karne ka view
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        
        response = JsonResponse({'qty': cart.__len__(), 'total': cart.get_total_price()})
        return response