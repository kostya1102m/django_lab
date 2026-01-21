from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_management, name='product_management'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<str:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<str:product_id>/delete/', views.delete_product, name='delete_product'),
]