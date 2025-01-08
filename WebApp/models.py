from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class ContactDb(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    mobile = models.CharField(max_length=15)
    place = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Register(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        return self.username
    
class CartDb(models.Model):
    Username = models.CharField(max_length=100, null=True, blank=True)
    ProductName = models.CharField(max_length=100, null=True, blank=True)
    Quantity = models.IntegerField(null=True, blank=True)
    Price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    TotalPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Prod_Image = models.ImageField(upload_to="Cart Images", null=True, blank=True)

class OrderDb(models.Model):
    FirstName = models.CharField(max_length=100, null=True, blank=True)  # New field for first name
    LastName = models.CharField(max_length=100, null=True, blank=True)   # New field for last name
    Email = models.EmailField(max_length=100, null=True, blank=True)
    Place = models.CharField(max_length=100, null=True, blank=True)
    Address = models.CharField(max_length=100, null=True, blank=True)
    Mobile = models.IntegerField(null=True, blank=True)
    State = models.CharField(max_length=100, null=True, blank=True)
    Pin = models.IntegerField(null=True, blank=True)
    TotalPrice = models.IntegerField(null=True, blank=True)
    Message = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.FirstName} {self.LastName} - {self.Email}"