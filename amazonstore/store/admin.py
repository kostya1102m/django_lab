from django.contrib import admin
from .models import (
    Customer, Seller, Brand, Category, Product,
    ProductSeller, Order, OrderItem
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('CustomerID', 'CustomerName', 'City', 'Country')
    search_fields = ('CustomerName', 'CustomerID')
    list_filter = ('Country', 'State')


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('SellerID',)
    search_fields = ('SellerID',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'BrandName')
    search_fields = ('BrandName',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'CategoryName')
    search_fields = ('CategoryName',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('ProductID', 'ProductName', 'Brand', 'Category')
    search_fields = ('ProductName', 'ProductID')
    list_filter = ('Brand', 'Category')


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    list_display = ('product', 'seller', 'IsActive')
    list_filter = ('IsActive',)
    search_fields = ('product__ProductName', 'seller__SellerID')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('OrderID', 'OrderDate', 'customer', 'OrderStatus', 'TotalAmount')
    list_filter = ('OrderStatus', 'PaymentMethod', 'OrderDate')
    search_fields = ('OrderID', 'customer__CustomerName')
    date_hierarchy = 'OrderDate'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('OrderItemID', 'order', 'product', 'Quantity', 'LineTotal')
    search_fields = ('order__OrderID', 'product__ProductName')
    list_filter = ('product__Category',)