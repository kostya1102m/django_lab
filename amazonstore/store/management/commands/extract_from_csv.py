import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import (
    Customer, Seller, Brand, Category, Product, 
    ProductSeller, Order, OrderItem
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the csv file')

    @transaction.atomic
    def handle(self, *args, **options):
        path = options['csv_file']
        
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        # Словари для кэширования
        brands_cache = {}
        categories_cache = {}
        sellers_cache = {}
        customers_cache = {}
        products_cache = {}
        
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            total_rows = sum(1 for _ in open(path, 'r', encoding='utf-8')) - 1
            
            self.stdout.write(self.style.SUCCESS(f'Found {total_rows} rows to import'))
            
            for i, row in enumerate(reader, 1):
                if i % 100 == 0:
                    self.stdout.write(f'Processing row {i}/{total_rows}...')
                
                # 1. Customer
                customer_id = row['CustomerID']
                if customer_id not in customers_cache:
                    customer, created = Customer.objects.get_or_create(
                        CustomerID=customer_id,
                        defaults={
                            'CustomerName': row['CustomerName'],
                            'City': row['City'],
                            'State': row['State'],
                            'Country': row['Country']
                        }
                    )
                    customers_cache[customer_id] = customer
                
                # 2. Seller
                seller_id = row['SellerID']
                if seller_id not in sellers_cache:
                    seller, created = Seller.objects.get_or_create(
                        SellerID=seller_id
                    )
                    sellers_cache[seller_id] = seller
                
                # 3. Brand
                brand_name = row['Brand']
                if brand_name not in brands_cache:
                    brand, created = Brand.objects.get_or_create(
                        BrandName=brand_name
                    )
                    brands_cache[brand_name] = brand
                
                # 4. Category
                category_name = row['Category']
                if category_name not in categories_cache:
                    category, created = Category.objects.get_or_create(
                        CategoryName=category_name
                    )
                    categories_cache[category_name] = category
                
                # 5. Product
                product_id = row['ProductID']
                if product_id not in products_cache:
                    product, created = Product.objects.get_or_create(
                        ProductID=product_id,
                        defaults={
                            'ProductName': row['ProductName'],
                            'Brand': brands_cache[brand_name],
                            'Category': categories_cache[category_name]
                        }
                    )
                    products_cache[product_id] = product
                
                # 6. ProductSeller
                ProductSeller.objects.get_or_create(
                    product=products_cache[product_id],
                    seller=sellers_cache[seller_id]
                )
                
                # 7. Order
                order, order_created = Order.objects.get_or_create(
                    OrderID=row['OrderID'],
                    defaults={
                        'OrderDate': datetime.strptime(row['OrderDate'], '%Y-%m-%d').date(),
                        'customer': customers_cache[customer_id],
                        'PaymentMethod': row['PaymentMethod'],
                        'OrderStatus': row['OrderStatus'],
                        'ShippingCost': float(row['ShippingCost']),
                        'TotalAmount': float(row['TotalAmount'])
                    }
                )
                
                # 8. OrderItem
                if order_created:  # Создаем OrderItem только если Order был создан
                    OrderItem.objects.create(
                        order=order,
                        product=products_cache[product_id],
                        seller=sellers_cache[seller_id],
                        Quantity=int(row['Quantity']),
                        UnitPrice=float(row['UnitPrice']),
                        Discount=float(row['Discount']),
                        Tax=float(row['Tax']),
                        LineTotal=(
                            float(row['Quantity']) * float(row['UnitPrice']) *
                            (1 - float(row['Discount'])) +
                            float(row['Tax']) +
                            float(row['ShippingCost'])
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {total_rows} rows!'))
        self.stdout.write(self.style.SUCCESS(f'Total records created:'))
        self.stdout.write(f'  Customers: {Customer.objects.count()}')
        self.stdout.write(f'  Sellers: {Seller.objects.count()}')
        self.stdout.write(f'  Brands: {Brand.objects.count()}')
        self.stdout.write(f'  Categories: {Category.objects.count()}')
        self.stdout.write(f'  Products: {Product.objects.count()}')
        self.stdout.write(f'  ProductSellers: {ProductSeller.objects.count()}')
        self.stdout.write(f'  Orders: {Order.objects.count()}')
        self.stdout.write(f'  OrderItems: {OrderItem.objects.count()}')