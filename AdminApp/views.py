from django.shortcuts import render, redirect
from .models import Category, Product
from WebApp.models import ContactDb
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime

def delete_contact(request, id):
    contact = ContactDb.objects.get(id=id)
    contact.delete()
    return redirect('AdminApp:display_contact_details')


def display_contact_details(request):
    contacts = ContactDb.objects.all()
    return render(request, 'contact_details.html', {'contacts': contacts})

def admin_logout(request):
    del request.session['username']
    # del request.session['password']
    messages.success(request, "You have been logged out successfully.")
    return redirect('AdminApp:admin_login')


def admin_login(request):
    messages.get_messages(request)
    return render(request, 'admin_login.html', {})

def admin_l(request):
    if request.method == "POST":
        print("Login attempt")  # Debugging line
        un = request.POST.get('username')
        pwd = request.POST.get('password')
        print(f"Username: {un}, Password: {pwd}")  # Debugging line
        # Check if the user exists
        user = User.objects.filter(username=un).first()
        if user:
            x = authenticate(username=un, password=pwd)
            if x is not None:
                login(request, x)
                request.session['username'] = un
                return redirect('AdminApp:index')  # Redirect to index after successful login
            else:
                messages.warning(request, "Invalid Password")
                return redirect('AdminApp:admin_login')
        else:
            messages.warning(request, 'Invalid username. Please try again.')
            return redirect('AdminApp:admin_login')
    else:
        return redirect('AdminApp:admin_login')

def index(request):
    # Check if the user is logged in and display a welcome message
    if 'username' in request.session:
        messages.success(request, "Welcome to LUJO AdminDashboard")
    
    categories = Category.objects.all()  # Get all categories
    products = Product.objects.count()  # Get the count of products
    x = datetime.now()

    # Generate date ranges
    current_year = x.year
    date_ranges = [
        (datetime.strptime(f"{current_year}-03-01", "%Y-%m-%d"), datetime.strptime(f"{current_year}-06-30", "%Y-%m-%d")),  # March - June
        (datetime.strptime(f"{current_year}-06-01", "%Y-%m-%d"), datetime.strptime(f"{current_year}-08-31", "%Y-%m-%d")),  # June - August
        (datetime.strptime(f"{current_year}-08-01", "%Y-%m-%d"), datetime.strptime(f"{current_year}-11-30", "%Y-%m-%d")),  # August - November
    ]

    return render(request, 'index.html', {
        'categories': categories,  # Pass the actual category objects
        'category_count': categories.count(),  # Pass the count separately
        'products': products,
        'x': x,
        'date_ranges': date_ranges,
        'is_category_page': True,
        'is_product_page': True,
        'is_home_page': True,
    })

def category_view(request, category_id):
    category = Category.objects.get(id=category_id)
    return render(request, 'category.html', {'category': category})

def add_category_view(request):
    # Clear any messages before rendering the add category page
    messages.get_messages(request)  # This will clear any existing messages
    if request.method == 'POST':
        print("Form submitted")  # Debug
        name = request.POST['name']
        description = request.POST['description']
        image = request.FILES['image']

        new_category = Category(name=name, description=description, image=image)
        new_category.save()
        messages.success(request, 'Category added successfully!')
        return redirect('AdminApp:display_categories_with_alert')  # Redirect to a new view
    return render(request, 'addcategory.html')

def display_categories_with_alert(request):
    categories = Category.objects.all()
    success_message = messages.get_messages(request)  # Get messages to pass to the template
    return render(request, 'displaycategory.html', {'categories': categories, 'success_message': success_message})


def display_categories(request):
    categories = Category.objects.all()
    return render(request, 'displaycategory.html', {'categories': categories})

def edit_category(request, id):
    category = Category.objects.get(id=id)

    if request.method == 'POST':
        category.name = request.POST['name']
        category.description = request.POST['description']
        
        # Check if a new image is uploaded
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('AdminApp:display_categories')

    return render(request, 'editcategory.html', {'category': category})

def delete_category(request, id):
    try:
        category = Category.objects.get(id=id)
        category.delete()  # Delete the category
        messages.success(request, 'Category deleted successfully!')  # Add success message
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
    return redirect('AdminApp:display_categories_with_alert')  # Redirect to a view that can show the message

def add_product(request):
    if request.method == 'POST':
        category_id = request.POST['category']
        name = request.POST['name']
        price = request.POST['price']
        description = request.POST['description']
        quantity = request.POST['quantity']
        image = request.FILES['image']

        # Create a new product instance
        new_product = Product(
            category_id=category_id,
            name=name,
            price=price,
            description=description,
            quantity=quantity,
            image=image
        )
        new_product.save()
        messages.success(request, 'Product added successfully!')
        return redirect('AdminApp:displayproducts')

    categories = Category.objects.all()
    return render(request, 'addproduct.html', {'categories': categories})

def display_products(request):
    products = Product.objects.all()
    return render(request, 'displayproduct.html', {'products': products})

def edit_product(request, id):
    product = Product.objects.get(id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.quantity = request.POST['quantity']
        
        # Check if a new image is uploaded
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        # Update the category
        product.category_id = request.POST['category']
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('AdminApp:displayproducts')

    return render(request, 'editproduct.html', {'product': product, 'categories': categories})

def delete_product(request, id):
    product = Product.objects.get(id=id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('AdminApp:displayproducts')

    return render(request, 'deleteproduct.html', {'product': product})