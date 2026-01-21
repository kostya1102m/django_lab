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


