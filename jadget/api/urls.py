from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view()),
    path('products/', get_create_products),
    path('products/<int:pk>/', get_edit_delete_product),
    path('order/', create_order),
    path('cart/add/<int:product_id>/', add_to_cart)
]