from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('search/',views.search_view,name='search'),
    path('checkout/',views.checkout,name='checkout'),
    path('update_item/',views.updateItem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),
    path('signup/', views.signup_view, name='signup'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
    path('<slug:slug>/',views.product_detail,name='product_detail'),
    path('shop/<slug:category_slug>/',views.category_list,name='category_list'),
    
    
]