from django.shortcuts import render, redirect
from django.views import View
from AdminApp.models import Category, Product
from WebApp.models import ContactDb, Register, CartDb, OrderDb
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
import razorpay 
import logging
logger = logging.getLogger(__name__)
# Create your views here. 
# def payment_success(request):
#     payment_id = request.POST.get('razorpay_payment_id')
#     order_id = request.POST.get('razorpay_order_id')
#     signature = request.POST.get('razorpay_signature')

#     # Verify the payment signature
#     client = razorpay.Client(auth=('rzp_test_BPXPob227YrMYQ', 'uAFvStGyR5HVF73EVuqp4UtQ'))
#     try:
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': order_id,
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': signature
#         })

#         # Payment is successful, clear the cart
#         username = request.session.get('username')
#         CartDb.objects.filter(Username=username).delete()  # Clear the cart items

#         messages.success(request, "Payment successful! Your order has been placed.")
#         return redirect('WebApp:order_success')  # Redirect to a success page

#     except Exception as e:
#         messages.error(request, "Payment verification failed. Please try again.")
#         return redirect('WebApp:payment')  # Redirect back to payment page



def get_cart_count(request): 
    """Get the count of items in the user's cart."""
    username = request.session.get('username')  # Get the username from the session
    if username:
        cart_items = CartDb.objects.filter(Username=username)
        return cart_items.count()  # Return the count of items in the cart
    return 0  # Return 0 if the user is not logged in


def payment(request):
    username = request.session.get('username')  # Get username from session
    if request.method == "POST":
        client = razorpay.Client(auth=('rzp_test_BPXPob227YrMYQ', 'uAFvStGyR5HVF73EVuqp4UtQ'))
        
        # Calculate total price from cart items
        cart_items = CartDb.objects.filter(Username=username)
        logger.debug(f"Cart items for user {username}: {[item.ProductName for item in cart_items]}")  # Log cart items
        
        if not cart_items.exists():
            logger.error("Cart is empty. Cannot proceed with payment.")
            return render(request, "payment.html", {'error': 'Your cart is empty. Please add items to your cart.'})

        # Calculate subtotal
        sub_total = sum(item.TotalPrice for item in cart_items)  # Calculate total price
        logger.debug(f"Subtotal calculated: {sub_total}")  # Log the subtotal
        
        # Calculate delivery charge
        if sub_total > 10000:
            shipping_amount = 100
        else:
            shipping_amount = 200
        
        total_price = sub_total + shipping_amount  # Total price including delivery charge
        logger.debug(f"Total price calculated (including shipping): {total_price}")  # Log the total price
        
        if total_price <= 0:
            logger.error("Total price is zero or negative. Cannot proceed with payment.")
            return render(request, "payment.html", {'error': 'Your cart is empty. Please add items to your cart.'})

        amount = int(total_price * 100)  # Convert to paisa (Razorpay expects amount in paisa)
        order_currency = 'INR' 

        try:
            payment_order = client.order.create({'amount': amount, 'currency': order_currency})
            logger.info("Razorpay payment order created: %s", payment_order)
            payment_id = payment_order.get('id')
            if payment_id:
                # Do not delete cart items here
                cart_count = get_cart_count(request)  # Get cart count
                return render(request, "payment.html", {
                    'payment_id': payment_id,
                    'username': username,
                    'cart_count': cart_count,
                    'amount': amount
                })
            else:
                logger.error("Payment order created but ID is missing: %s", payment_order)
                return render(request, "payment.html", {'error': 'Payment order created but ID is missing.'})
        except Exception as e:
            logger.error("Error creating Razorpay order: %s", e)
            return render(request, "payment.html", {'error': 'An error occurred while processing your payment. Please try again.'})

    cart_count = get_cart_count(request)  # Get cart count
    return render(request, "payment.html", {'username': username, 'cart_count': cart_count})

def place_order(request):
    if request.method == "POST":
        # Get data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        country = request.POST.get('country')
        address = request.POST.get('address')
        apartment = request.POST.get('apartment', '')  # Optional field
        city = request.POST.get('city')
        state = request.POST.get('state')
        pin = request.POST.get('pin')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        message = request.POST.get('message', '')  # Optional field
        create_account = request.POST.get('create_account')  # Checkbox
        password = request.POST.get('password') if create_account else None  # Only if creating an account

        # Debugging: Print the values to the console
        print(f"First Name: {first_name}, Last Name: {last_name}, Email: {email}, Address: {address}, Mobile: {mobile}")

        # Calculate total price from cart items
        username = request.session.get('username')
        cart_items = CartDb.objects.filter(Username=username)
        total_price = sum(item.TotalPrice for item in cart_items)

        # Create an OrderDb instance
        order = OrderDb(
            FirstName=first_name,  # Save first name
            LastName=last_name,    # Save last name
            Email=email,
            Place=country,  # Assuming 'Place' refers to the country
            Address=address,
            Mobile=mobile,
            State=state,
            Pin=pin,
            TotalPrice=total_price,
            Message=message
        )

        try:
            order.save()  # Save the order to the database
            messages.success(request, "Your order has been placed successfully!")
            return redirect('WebApp:payment')  # Redirect to a success page or home page
        except Exception as e:
            messages.error(request, f"An error occurred while placing your order: {e}")
            return redirect('WebApp:checkout')  # Redirect back to checkout on error

    return redirect('WebApp:checkout')  # Redirect if not a POST request



def checkout(request):
    shipping_amount = 0
    total = 0
    sub_total = 0
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    
    # Fetch cart items for the logged-in user
    cart_items = CartDb.objects.filter(Username=username)
    # Count the number of items in the cart
    cart_count = cart_items.count()
    
    # Calculate subtotal
    for item in cart_items:
        sub_total += item.TotalPrice
        if sub_total > 10000:
            shipping_amount = 100
        else:
            shipping_amount = 200
        total = sub_total + shipping_amount

    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
        'cart_items': cart_items,  # Pass the cart items to the template
        'cart_count': cart_count,
        'sub_total': sub_total,
        'shipping_amount': shipping_amount,
        'total': total,  # Add subtotal to the context
    }
    return render(request, "checkout.html", context)

def save_cart(request):
    if request.method == "POST":
        pname = request.POST.get('name')
        qty = request.POST.get('quantity')
        pri = request.POST.get('price')

        try:
            product = Product.objects.get(name=pname)  # Ensure this is the correct field
            img = product.image  # Assuming 'image' is the field in your Product model
        except Product.DoesNotExist:
            img = None
            messages.error(request, "Product does not exist.")
            return redirect("WebApp:home")

        # Convert to integers or decimals before saving
        qty = int(qty) if qty and qty.isdigit() else 0  # Default to 0 if qty is empty or not a digit
        pri = Decimal(pri) if pri and is_valid_decimal(pri) else Decimal('0.00')  # Default to 0.00 if price is invalid
        
        # Calculate total price for this item
        total_price = qty * pri
        
        # Attempt to save the object
        try:
            obj = CartDb(
                Username=request.session.get('username'),
                Prod_Image=img,  # Save the image here
                Quantity=qty,
                Price=pri,
                TotalPrice=total_price,
                ProductName=pname
            )
            obj.save()
            logger.debug(f"Added to cart: {pname}, Quantity: {qty}, Total Price: {total_price}")
            messages.success(request, "Item added to cart successfully!")
        except Exception as e:
            messages.error(request, f"Error saving item to cart: {e}")
            logger.error(f"Error saving item to cart: {e}")
            return redirect("WebApp:cart")

        return redirect("WebApp:home")

    # Handle GET request
    return redirect("WebApp:cart")

def is_valid_decimal(value):
    """Check if the value can be converted to a Decimal."""
    try:
        Decimal(value)
        return True
    except (InvalidOperation, ValueError):
        return False



def cart(request):
    shipping_amount = 0
    total = 0
    sub_total = 0
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    
    # Fetch cart items for the logged-in user
    cart_items = CartDb.objects.filter(Username=username)
    # Count the number of items in the cart
    cart_count = cart_items.count()
    
    # Check if the cart is empty
    if cart_count == 0:
        messages.info(request, "Your cart is empty. Please add items to your cart.")
        return render(request, "cart.html", {'username': username, 'categories': categories, 'cart_count': cart_count})

    # Calculate subtotal
    for item in cart_items:
        sub_total += item.TotalPrice
        if sub_total > 10000:
            shipping_amount = 100
        else:
            shipping_amount = 200
        total = sub_total + shipping_amount

        # Log the item and its image
        logger.debug(f"Cart item: {item.ProductName}, Image: {item.Prod_Image}")

    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
        'cart_items': cart_items,  # Pass the cart items to the template
        'cart_count': cart_count,
        'sub_total': sub_total,
        'shipping_amount': shipping_amount,
        'total': total,  # Add subtotal to the context
    }
    
    return render(request, "cart.html", context) 


def remove_from_cart(request, item_id):
    try:
        item = CartDb.objects.get(id=item_id)
        item.delete()
        messages.success(request, "Item removed from cart successfully!")
    except CartDb.DoesNotExist:
        messages.error(request, "Item not found in cart.")
    
    return redirect("WebApp:cart")

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Register.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['username'] = user.username  # Ensure this is set
                messages.success(request, "Welcome to Lujo app, your perfect shopping place.")
                return redirect('WebApp:home')
        except Register.DoesNotExist:
            messages.error(request, "Invalid username or password.")
    return render(request, "user_login.html")

def user_logout(request):
    request.session.flush()  # Clear the session data
    messages.info(request, "You are logged out of the Lujo app. Please log in again.")
    return redirect('WebApp:login')



def homepage(request):
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    # Fetch cart items for the logged-in user
    cart_items = CartDb.objects.filter(Username=username)
    cart_count = cart_items.count()
    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
        'cart_items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, "home.html", context)

def aboutow(request):
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
    }
    return render(request, "about.html", context)

def contactow(request):
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
    }
    return render(request, "contact.html", context)

def save_contact(request):
    if request.method == "POST":
        na = request.POST.get('name')
        em = request.POST.get('email')
        msg = request.POST.get('message')
        ph = request.POST.get('mobile')
        pl = request.POST.get('place')
        obj = ContactDb(name=na, email=em, message=msg, mobile=ph, place=pl)
        obj.save()
        messages.success(request, "Your message has been sent successfully!")
        return redirect('WebApp:contact')

def our_products(request):
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    products = Product.objects.all()
    cart_items = CartDb.objects.filter(Username=username)
    cart_count = cart_items.count()
    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
        'products': products,
        'cart_items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, "allproducts.html", context)

def filtered(request, cat_name):
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    products = Product.objects.filter(category__name=cat_name)
    cart_items = CartDb.objects.filter(Username=username)
    cart_count = cart_items.count()
    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
        'products': products,
        'cart_items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, "filtered_products.html", context)

def singleproduct(request, id):
    username = request.session.get('username')  # Get the username from the session
    categories = Category.objects.all()
    product = Product.objects.get(id=id)
    context = {
        'username': username,  # Pass the username to the template
        'categories': categories,
        'product': product,
    }
    return render(request, "singleproduct.html", context)

def user_register(request):
    logger.debug("Registration request received.")
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        logger.debug(f"Username: {username}, Email: {email}, Phone: {phone}, Password: {password}, Confirm Password: {confirmpassword}")

        # Basic validation
        if password != confirmpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('WebApp:register')  # Redirect back to registration form

        # Check if the user already exists
        if Register.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('WebApp:register')

        if Register.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('WebApp:register')

        # Save to the database with hashed password
        user = Register(
            username=username,
            email=email,
            phone=phone,
            password=make_password(password)
        )
        try:
            user.save()
            logger.debug("User saved successfully!")
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            messages.error(request, "An error occurred during registration.")
            return redirect('WebApp:register')
        messages.success(request, "Registration successful!")
        return redirect('WebApp:login')  # Redirect to login page after successful registration

    return render(request, "user_reg.html")  # Render the registration page for GET requests
