from django.contrib import admin
from .models import Category, Product  # Import your model

# Register your model with the admin site
admin.site.register(Category)
admin.site.register(Product)