from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.http import JsonResponse
import json
import datetime;
from .utils import *
from .forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib import messages


# Create your views here.

def store(request):
    products=Product.objects.all()
    categories=Category.objects.all()
    data=cartData(request)
    cartItems = data['cartItems']
    
    context={'products':products,'categories':categories,'cartItems':cartItems,'shipping':False}
    return render(request,'store/store.html',context)

def search_view(request):
    query=request.GET["query"]
    products=Product.objects.all().filter(title__icontains=query)
    categories=Category.objects.all()
    data=cartData(request)
    cartItems = data['cartItems']
    
    context={'products':products,'categories':categories,'cartItems':cartItems,'shipping':False}
    return render(request,'store/store.html',context)

def category_list(request,category_slug):
    category=get_object_or_404(Category,slug=category_slug)
    products=Product.objects.filter(category=category)
    categories=Category.objects.all()
    data=cartData(request)
    cartItems = data['cartItems']
   
        
    context={'products':products,'categories':categories,'category':category,'cartItems':cartItems,'shipping':False}
    return render(request,'store/category_list.html',context)
    

def product_detail(request,slug):
    product=get_object_or_404(Product,slug=slug)
    categories=Category.objects.all()
    data=cartData(request)
    cartItems = data['cartItems']
   
        
    context={'product':product,'categories':categories,'cartItems':cartItems,'shipping':False}
    return render(request,'store/product_detail.html',context)
 
def cart(request):
    categories=Category.objects.all()
    data=cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
   
        
            
    context={'categories':categories,'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'store/cart.html',context)
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def checkout(request):
    categories=Category.objects.all()
    data=cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    
    context={'categories':categories,'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'store/checkout.html',context)
    
    
def product_detail(request,slug):
    product=get_object_or_404(Product,slug=slug)
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        cookieData=cookieCart(request)
        cartItems=cookieData['cartItems']
        
        
    context={'product':product,'cartItems':cartItems,'shipping':False}
    return render(request,'store/product_detail.html',context)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
 
   
    
    return JsonResponse("Item was added",safe=False)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
       
    else:
        customer,order=guestOrder(request,data) 
      
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == order.get_cart_total:
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                )
       
            
    return JsonResponse("Payment Complete ",safe=False)


def signup_view(request):
    categories=Category.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save()
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            

            messages.success(request, 'You have successfully signed up!')
            return redirect('login')  # Redirect to the customer's profile or any other page you want
        else:
            # Display form errors as messages
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f'{user_form.fields[field].label}: {error}')

            for field, errors in customer_form.errors.items():
                for error in errors:
                    messages.error(request, f'{customer_form.fields[field].label}: {error}')
    else:
        user_form = UserRegistrationForm()
        customer_form = CustomerForm()
    
    context={'items':items,'categories':categories,'order':order,'cartItems':cartItems,'shipping':'False','user_form': user_form, 'customer_form': customer_form}    

        
    return render(request, 'store/signup.html',context)


def login_view(request):
    categories=Category.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect('store')  # Redirect to the customer's profile or any other page you want
            else:
                form.add_error(None, "Invalid username or password.")
                messages.error(request, 'Login failed. Please check your credentials and try again.')
    else:
        form = LoginForm()
        
    context={'form': form,'items':items,'categories':categories,'order':order,'cartItems':cartItems,'shipping':'False'}
    return render(request, 'store/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('store') 