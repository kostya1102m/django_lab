from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Max, Min
from django.db.models.functions import TruncMonth
from .models import (
    Customer, Seller, Brand, Category, Product, 
    ProductSeller, Order, OrderItem
)


def index(request):
    # Основные таблицы
    customers = Customer.objects.all()[:50]
    sellers = Seller.objects.all()[:50]
    brands = Brand.objects.all()[:50]
    categories = Category.objects.all()[:50]
    products = Product.objects.select_related('Brand', 'Category').all()[:50]
    orders = Order.objects.select_related('customer').all()[:50]
    
    # Статистика
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
    ).order_by('-count')
    
    payment_stats = Order.objects.values('PaymentMethod').annotate(
        count=Count('OrderID'),
        total=Sum('TotalAmount')
    ).order_by('-count')
    
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
    ).order_by('-month')[:12]
    
    context = {
        # Табличные данные
        'customers': customers,
        'sellers': sellers,
        'brands': brands,
        'categories': categories,
        'products': products,
        'orders': orders,
        
        # Статистика
        'order_stats': order_stats,
        'status_stats': status_stats,
        'payment_stats': payment_stats,
        'top_products': top_products,
        'top_customers': top_customers,
        'monthly_sales': monthly_sales,
        
        # Счетчики
        'total_customers': Customer.objects.count(),
        'total_sellers': Seller.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_revenue': order_stats.get('total_revenue', 0) or 0,
    }
    
    return render(request, 'index.html', context)