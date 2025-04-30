from django.urls import path
from . import views


urlpatterns = [
    # ...existing URLs...
    path('add-to-cart/<str:product_name>/<str:price>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
]