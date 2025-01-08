from django.urls import path
from .views import index, category_view, add_category_view, display_categories, edit_category, delete_category, add_product, display_products, edit_product, delete_product, admin_login, admin_l, admin_logout, display_contact_details, delete_contact, display_categories_with_alert
# from . import views
app_name = 'AdminApp'
urlpatterns = [
    path('index/', index, name='index'),
    path('admin_login/', admin_login, name='admin_login'),
    path('admin_l/', admin_l, name='admin_l'),
    path('admin_logout/', admin_logout, name='admin_logout'),
    path('category/<int:category_id>/', category_view, name='category'),
    path('category/add/', add_category_view, name='add_category'),
    path('display-categories/', display_categories, name='display_categories'),
    path('edit-category/<int:id>/', edit_category, name='edit_category'),
    path('delete-category/<int:id>/', delete_category, name='delete_category'),
    path('addproduct/', add_product, name='addproduct'),
    path('displayproducts/', display_products, name='displayproducts'),
    path('products/edit/<int:id>/', edit_product, name='edit_product'),
    path('products/delete/<int:id>/', delete_product, name='delete_product'),
    path('contact/details/', display_contact_details, name='display_contact_details'),
    path('contact/delete/<int:id>/', delete_contact, name='delete_contact'),  # Ensure this line exists
    path('display-categories-with-alert/', display_categories_with_alert, name='display_categories_with_alert'),
]