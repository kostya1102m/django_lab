from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator

class Customer(models.Model):
    CustomerID = models.CharField(max_length=20, primary_key=True)
    CustomerName = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    State = models.CharField(max_length=255)
    Country = models.CharField(max_length=255)


    class Meta:
        db_table = 'Customers'
        ordering = ['CustomerName']
    
    def __str__(self):
        return f"{self.CustomerID} - {self.CustomerName}"
    

class Seller(models.Model):
    SellerID = models.CharField(max_length=20, primary_key=True)
    SellerName = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Sellers'

    def __str__(self):
        return self.SellerID
    

class Brand(models.Model):
    BrandName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'Brands'

    def __str__(self):
        return self.BrandName
    

class Category(models.Model):
    CategoryName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'Categories'
        verbose_name_plural = 'Categories'
        ordering = ['CategoryName']

    def __str__(self):
        return self.CategoryName


class Product(models.Model):
    ProductID = models.CharField(max_length=20, primary_key=True)
    ProductName = models.CharField(max_length=255)
    Brand = models.ForeignKey(Brand, on_delete=models.CASCADE, db_column='BrandID')
    Category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='CategoryID')

    class Meta:
        db_table = 'Products'
        ordering = ['ProductName']

    def __str__(self):
        return f"{self.ProductName} ({self.ProductID})"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Delivered', 'Delivered'),
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Debit Card', 'Debit Card'),
        ('Credit Card', 'Credit Card'),
        ('Amazon Pay', 'Amazon Pay'),
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking'),
        ('Cash on Delivery', 'Cash on Delivery'),
    ]

    OrderID = models.CharField(max_length=20, primary_key=True)
    OrderDate = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='CustomerID')
    PaymentMethod = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    OrderStatus = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    ShippingCost = models.DecimalField(max_digits=10, decimal_places=2)
    TotalAmount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'Orders'
        ordering = ['-OrderDate']

    def __str__(self):
        return f"Order {self.OrderID} - {self.OrderStatus}"


class OrderItem(models.Model):
    OrderItemID = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='OrderID')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='ProductID')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, db_column='SellerID')
    Quantity = models.IntegerField()
    UnitPrice = models.DecimalField(max_digits=10, decimal_places=2)
    Discount = models.DecimalField(max_digits=5, decimal_places=4, 
                                   validators=[MinValueValidator(0), MaxValueValidator(1)])
    Tax = models.DecimalField(max_digits=10, decimal_places=2)
    LineTotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'OrderItems'
        unique_together = ('order', 'product', 'seller')

    def __str__(self):
        return f"OrderItem {self.OrderItemID} for {self.order.OrderID}"