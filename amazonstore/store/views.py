from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg, Max, Min
from django.db.models.functions import TruncMonth
from .models import (
    Customer, Seller, Brand, Category, Product, 
    ProductSeller, Order, OrderItem
)


def index(request):
    page_customers = request.GET.get('page_customers', 1)
    page_orders = request.GET.get('page_orders', 1)
    page_products = request.GET.get('page_products', 1)
    page_sellers = request.GET.get('page_sellers', 1)
    
    items_per_page = 20 
    
    
    customers_all = Customer.objects.all().order_by('CustomerID')
    customers_paginator = Paginator(customers_all, items_per_page)
    customers_page = customers_paginator.get_page(page_customers)
    
    
    sellers_all = Seller.objects.all().order_by('SellerID')
    sellers_paginator = Paginator(sellers_all, items_per_page)
    sellers_page = sellers_paginator.get_page(page_sellers)
    
    
    brands_all = Brand.objects.all().order_by('BrandName')
    brands_paginator = Paginator(brands_all, items_per_page)
    brands_page = brands_paginator.get_page(1)
    
    
    categories_all = Category.objects.all().order_by('CategoryName')
    categories_paginator = Paginator(categories_all, items_per_page)
    categories_page = categories_paginator.get_page(1)
    
    
    products_all = Product.objects.select_related('Brand', 'Category').all().order_by('ProductID')
    products_paginator = Paginator(products_all, items_per_page)
    products_page = products_paginator.get_page(page_products)
    
    
    orders_all = Order.objects.select_related('customer').all().order_by('-OrderDate')
    orders_paginator = Paginator(orders_all, items_per_page)
    orders_page = orders_paginator.get_page(page_orders)
    
    
    order_stats = Order.objects.aggregate(
        total_orders=Count('OrderID'),
        total_revenue=Sum('TotalAmount'),
        avg_order_value=Avg('TotalAmount'),
        max_order=Max('TotalAmount'),
        min_order=Min('TotalAmount')
    )
    
    status_stats = Order.objects.values('OrderStatus').annotate(
        count=Count('OrderID'),
        total=Sum('TotalAmount')
    ).order_by('-count')[:5]
    
    payment_stats = Order.objects.values('PaymentMethod').annotate(
        count=Count('OrderID'),
        total=Sum('TotalAmount')
    ).order_by('-count')[:5] 
    
    top_products = OrderItem.objects.values(
        'product__ProductName'
    ).annotate(
        total_quantity=Sum('Quantity'),
        total_revenue=Sum('LineTotal')
    ).order_by('-total_quantity')[:10]
    
    top_customers = Order.objects.values(
        'customer__CustomerName', 'customer__Country'
    ).annotate(
        total_orders=Count('OrderID'),
        total_spent=Sum('TotalAmount')
    ).order_by('-total_spent')[:10]
    
    monthly_sales = Order.objects.annotate(
        month=TruncMonth('OrderDate')
    ).values('month').annotate(
        orders=Count('OrderID'),
        revenue=Sum('TotalAmount')
    ).order_by('-month')[:6] 
    
    context = {
        # paginated objects
        'customers': customers_page,
        'sellers': sellers_page,
        'brands': brands_page,
        'categories': categories_page,
        'products': products_page,
        'orders': orders_page,
        
        # pagination
        'customers_paginator': customers_paginator,
        'sellers_paginator': sellers_paginator,
        'brands_paginator': brands_paginator,
        'categories_paginator': categories_paginator,
        'products_paginator': products_paginator,
        'orders_paginator': orders_paginator,
        
        
        'current_page_customers': page_customers,
        'current_page_orders': page_orders,
        'current_page_products': page_products,
        'current_page_sellers': page_sellers,
        
        # Статистика
        'order_stats': order_stats,
        'status_stats': status_stats,
        'payment_stats': payment_stats,
        'top_products': top_products,
        'top_customers': top_customers,
        'monthly_sales': monthly_sales,
        
        
        'total_customers': Customer.objects.count(),
        'total_sellers': Seller.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_revenue': order_stats.get('total_revenue', 0) or 0,
        
        
        'items_per_page': items_per_page,
    }
    
    return render(request, 'index.html', context)