from django.urls import path
from WebApp import views
app_name = 'WebApp'
urlpatterns=[
    path('home/', views.homepage, name='home'),
    path('about/', views.aboutow, name='about'),
    path('contact/', views.contactow, name='contact'),
    path('contact/save/', views.save_contact, name='save_contact'),
    path('allproduct/', views.our_products, name='allproduct'),
    path('filter/<cat_name>/', views.filtered, name='filter'),
    path('single/<int:id>/', views.singleproduct, name='single'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('cart/', views.cart, name='cart'),
    path('save_cart/', views.save_cart, name='save_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('payment/', views.payment, name='payment'),
]
