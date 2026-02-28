from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_home, name='store'),
    # Naya AJAX URL yahan add kiya
    path('ajax/search/', views.search_products_ajax, name='ajax_search'), 
    path('category/<slug:category_slug>/', views.store_home, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('search/', views.search, name='search'),
]
