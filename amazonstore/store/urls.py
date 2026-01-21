from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_management, name='product_management'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<str:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<str:product_id>/', views.delete_product, name='delete_product'),
]