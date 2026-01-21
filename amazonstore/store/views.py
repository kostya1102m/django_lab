from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg, Max, Min, Q
from django.db.models.functions import TruncMonth
from datetime import datetime
from .models import (
    Customer, Seller, Brand, Category, Product, 
    ProductSeller, Order, OrderItem
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


def format_currency(value):
    try:
        return f"${float(value):.2f}"
    except:
        return "$0.00"


def get_order_status_badge(status):
    badge_class = {
        'Delivered': 'status-delivered',
        'Pending': 'status-pending',
        'Shipped': 'status-shipped',
        'Cancelled': 'status-cancelled',
        'Returned': 'status-returned'
    }
    return f'<span class="status-badge {badge_class.get(status, "status-returned")}">{status}</span>'


def index(request):
    page_customers = request.GET.get('page_customers', 1)
    page_orders = request.GET.get('page_orders', 1)
    page_products = request.GET.get('page_products', 1)
    page_sellers = request.GET.get('page_sellers', 1)
    
    items_per_page = 20
    
    extra_params = {}
    if page_customers != '1':
        extra_params['page_customers'] = page_customers
    if page_orders != '1':
        extra_params['page_orders'] = page_orders
    if page_products != '1':
        extra_params['page_products'] = page_products
    if page_sellers != '1':
        extra_params['page_sellers'] = page_sellers
    
    customers_all = Customer.objects.all().order_by('CustomerID')
    customers_paginator = Paginator(customers_all, items_per_page)
    customers_page = customers_paginator.get_page(page_customers)
    
    customers_data = {
        'headers': ['ID', 'Name', 'City', 'Country'],
        'rows': [
            [customer.CustomerID, customer.CustomerName, customer.City, customer.Country]
            for customer in customers_page
        ],
        'page_obj': customers_page,
        'extra_params': {k: v for k, v in extra_params.items() if k != 'page_customers'}
    }
    
    sellers_all = Seller.objects.all().order_by('SellerID')
    sellers_paginator = Paginator(sellers_all, items_per_page)
    sellers_page = sellers_paginator.get_page(page_sellers)
    
    sellers_data = {
        'headers': ['Seller ID', 'Name'],
        'rows': [
            [seller.SellerID, seller.SellerName or f"Seller {seller.SellerID}"]
            for seller in sellers_page
        ],
        'page_obj': sellers_page,
        'extra_params': {k: v for k, v in extra_params.items() if k != 'page_sellers'}
    }
    
    products_all = Product.objects.select_related('Brand', 'Category').all().order_by('ProductID')
    products_paginator = Paginator(products_all, items_per_page)
    products_page = products_paginator.get_page(page_products)
    
    products_data = {
        'headers': ['Product ID', 'Name', 'Brand', 'Category'],
        'rows': [
            [product.ProductID, product.ProductName, product.Brand.BrandName, product.Category.CategoryName]
            for product in products_page
        ],
        'page_obj': products_page,
        'extra_params': {k: v for k, v in extra_params.items() if k != 'page_products'}
    }
    
    orders_all = Order.objects.select_related('customer').all().order_by('-OrderDate')
    orders_paginator = Paginator(orders_all, items_per_page)
    orders_page = orders_paginator.get_page(page_orders)
    

    orders_rows = [
        [
            order.OrderID,
            order.OrderDate.strftime('%Y-%m-%d'),
            order.customer.CustomerName,
            get_order_status_badge(order.OrderStatus),
            format_currency(order.TotalAmount) 
        ]
        for order in orders_page
    ]
    
    orders_data = {
        'headers': ['Order ID', 'Date', 'Customer', 'Status', 'Amount'],
        'rows': orders_rows,
        'page_obj': orders_page,
        'extra_params': {k: v for k, v in extra_params.items() if k != 'page_orders'}
    }
    
    
    order_stats = Order.objects.aggregate(
        total_orders=Count('OrderID'),
        total_revenue=Sum('TotalAmount'),
        avg_order_value=Avg('TotalAmount'),
        max_order=Max('TotalAmount'),
        min_order=Min('TotalAmount')
    )
    
    
    total_revenue_formatted = format_currency(order_stats.get('total_revenue', 0) or 0)
    avg_order_value_formatted = format_currency(order_stats.get('avg_order_value', 0) or 0)
    
   
    status_stats_data = Order.objects.values('OrderStatus').annotate(
        count=Count('OrderID'),
        total=Sum('TotalAmount')
    ).order_by('-count')
    
    status_stats_rows = [
        [stat['OrderStatus'], stat['count'], format_currency(stat['total'])]
        for stat in status_stats_data
    ]
    
    status_stats = {
        'headers': ['Status', 'Count', 'Total Amount'],
        'rows': status_stats_rows
    }
    
    
    payment_stats_data = Order.objects.values('PaymentMethod').annotate(
        count=Count('OrderID'),
        total=Sum('TotalAmount')
    ).order_by('-count')
    
    payment_stats_rows = [
        [stat['PaymentMethod'], stat['count'], format_currency(stat['total'])]
        for stat in payment_stats_data
    ]
    
    payment_stats = {
        'headers': ['Payment Method', 'Count', 'Total Amount'],
        'rows': payment_stats_rows
    }
    
    
    top_products_data = OrderItem.objects.values(
        'product__ProductName'
    ).annotate(
        total_quantity=Sum('Quantity'),
        total_revenue=Sum('LineTotal')
    ).order_by('-total_quantity')[:10]
    
    top_products_rows = [
        [item['product__ProductName'], item['total_quantity'], format_currency(item['total_revenue'])]
        for item in top_products_data
    ]
    
    top_products = {
        'headers': ['Product', 'Quantity Sold', 'Revenue'],
        'rows': top_products_rows
    }
    
    
    top_customers_data = Order.objects.values(
        'customer__CustomerName', 'customer__Country'
    ).annotate(
        total_orders=Count('OrderID'),
        total_spent=Sum('TotalAmount')
    ).order_by('-total_spent')[:10]
    
    top_customers_rows = [
        [item['customer__CustomerName'], item['customer__Country'], 
         item['total_orders'], format_currency(item['total_spent'])]
        for item in top_customers_data
    ]
    
    top_customers = {
        'headers': ['Customer', 'Country', 'Orders', 'Total Spent'],
        'rows': top_customers_rows
    }
    
    
    monthly_sales_data = Order.objects.annotate(
        month=TruncMonth('OrderDate')
    ).values('month').annotate(
        orders=Count('OrderID'),
        revenue=Sum('TotalAmount')
    ).order_by('-month')[:6]
    
    monthly_sales_rows = [
        [item['month'].strftime('%B %Y'), item['orders'], format_currency(item['revenue'])]
        for item in monthly_sales_data
    ]
    
    monthly_sales = {
        'headers': ['Month', 'Orders', 'Revenue'],
        'rows': monthly_sales_rows
    }
    
    context = {
        'total_customers': Customer.objects.count(),
        'total_sellers': Seller.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_revenue': total_revenue_formatted,  
        'order_stats': {
            'avg_order_value': avg_order_value_formatted,  
            'max_order': format_currency(order_stats.get('max_order', 0) or 0),
            'min_order': format_currency(order_stats.get('min_order', 0) or 0),
        },
        
        'customers_data': customers_data,
        'sellers_data': sellers_data,
        'products_data': products_data,
        'orders_data': orders_data, 
        
        'status_stats': status_stats, 
        'payment_stats': payment_stats, 
        'top_products': top_products, 
        'top_customers': top_customers, 
        'monthly_sales': monthly_sales, 
        
        'current_date': datetime.now().strftime('%B %d, %Y'), 
    }
    
    return render(request, 'index.html', context)


def product_management(request):
    search_query = request.GET.get('search', '')
    
    # Поиск по названию или ID продукта
    if search_query:
        products = Product.objects.filter(
            Q(ProductName__icontains=search_query) | 
            Q(ProductID__icontains=search_query)
        ).select_related('Brand', 'Category')
    else:
        products = Product.objects.all().select_related('Brand', 'Category')
    
    
    brands = Brand.objects.all()
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'product_management.html', context)


def add_product(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            product_id = request.POST.get('product_id')
            product_name = request.POST.get('product_name')
            brand_id = request.POST.get('brand_id')
            category_id = request.POST.get('category_id')
            
            # Проверяем, существует ли уже такой ID
            if Product.objects.filter(ProductID=product_id).exists():
                messages.error(request, f'Продукт с ID {product_id} уже существует!')
                return redirect('store:product_management')
            
            brand = Brand.objects.get(id=brand_id)
            category = Category.objects.get(id=category_id)
            
            # Создаем продукт
            Product.objects.create(
                ProductID=product_id,
                ProductName=product_name,
                Brand=brand,
                Category=category
            )
            
            messages.success(request, f'Продукт {product_name} успешно добавлен!')
            
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении продукта: {str(e)}')
        
        return redirect('store:product_management')
    
    return redirect('store:product_management')


def edit_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, ProductID=product_id)
            
            product.ProductName = request.POST.get('product_name')
            
            brand_id = request.POST.get('brand_id')
            category_id = request.POST.get('category_id')
            
            if brand_id:
                product.Brand = Brand.objects.get(id=brand_id)
            if category_id:
                product.Category = Category.objects.get(id=category_id)
            
            product.save()
            
            messages.success(request, f'Продукт {product.ProductName} успешно обновлен!')
            
        except Exception as e:
            messages.error(request, f'Ошибка при редактировании: {str(e)}')
        
        return redirect('store:product_management')
    
    return redirect('store:product_management')


def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, ProductID=product_id)
            product_name = product.ProductName
            product.delete()
            
            messages.success(request, f'Продукт {product_name} успешно удален!')
            
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
        
        return redirect('store:product_management')
    
    return redirect('store:product_management')