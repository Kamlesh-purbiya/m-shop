from .cart import Cart

def cart_context(request):
    # Ab hum 'cart' variable ko kisi bhi HTML file me use kar sakte hain
    return {'cart': Cart(request)}