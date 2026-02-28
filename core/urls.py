from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render # Ye add karein
from accounts import views as account_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    # path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', account_views.login, name='login'),
    path('register/', account_views.register, name='register'),
    path('logout/', account_views.logout, name='logout'),
    path('dashboard/', account_views.customer_dashboard, name='customer_dashboard'),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
] 
if settings.DEBUG or not settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)