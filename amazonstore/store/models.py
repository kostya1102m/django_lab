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
        return f"{self.CustomerName ({self.CustomerID})}"