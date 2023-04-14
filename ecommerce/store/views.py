from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

import json
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def store(request):
    category_id = request.GET.get('category')
    if category_id:
        category = Category.objects.get(id=category_id)
        products = Product.objects.filter(category=category_id)
        
        
    else:
        category = None
        
        products = Product.objects.all()
    
     
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        items = []
        cartItems = 0
        order = {'get_cart_total': 0, 'cartItems':cartItems,'shipping': False}
       

    categories = Category.objects.all()
    
    
    if 'q' in request.GET:
        query = request.GET['q']
        if query:
            products = products.filter(name__icontains=query)
    if 'price_range' in request.GET:
        price_range = request.GET['price_range']
        if price_range:
            if price_range == '1':
                products = products.filter(price__lte=100000)
            elif price_range == '2':
                products = products.filter(price__gt=100000, price__lte=500000)
            elif price_range == '3':
                products = products.filter(price__gt=500000, price__lte=1000000)
                
    paginator = Paginator(products, 6)  # Giới hạn 10 sản phẩm trên mỗi trang
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # Nếu page không phải là số nguyên, trả về trang đầu tiên
        products = paginator.page(1)
    except EmptyPage:
        # Nếu page lớn hơn số trang có sẵn, trả về trang cuối cùng
        products = paginator.page(paginator.num_pages)
    
    context = {'products': products, 'categories': categories, 'category': category, 'cartItems':cartItems}
    
    
    
    return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:#kiem tra xem nguoi dung da dang nhap vao trang web hay chua
        customer = request.user.customer#truy xuat doi tuong khach hang duoc lien ket voi nguoi dung
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        #Truy xuat mot don hang chua hoan chinh cho doi tuong khach hang cua nguoi dung da duoc xac thuc
        #Neu mot don hang nhu vay da ton tai thì sẽ lấy nó
        #Nếu không nó sẽ tạo một đơn đặt hàng mới với Plete được đặt thành false
        #Phương thức get_ỏ_create() trả về một bộ chứa đối tượng đươn hàng và một giá trị boolean cho biết đơn hàng đã được tạo hay truy xuất
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        #truy xuat tat ca cac muc trong don dat hang bang phuong thuc orderitem_set.all()
    else:
        try:
             cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        
        items = []
        order = {'get_cart_items':0, 'get_cart_total':0,'shipping': False}
        cartItems = order['get_cart_items']

        for i in cart:
            cartItems += cart[i]["quantity"]
            
            product = Product.objects.get(id = i)
            
            total = (product.price * cart[i]["quantity"])
            
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]["quantity"]
            
            item = {
            'product':{
                'id':product.id,
                'name':product.name,
                'price': product.price,
                'imageURL': product.imageURL,
            },
            'quantity':cart[i]["quantity"],
            'get_total':total
            }
            items.append(item)

            
            
           
  
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:#kiem tra xem nguoi dung da dang nhap vao trang web hay chua
        customer = request.user.customer#truy xuat doi tuong khach hang duoc lien ket voi nguoi dung
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        #Truy xuat mot don hang chua hoan chinh cho doi tuong khach hang cua nguoi dung da duoc xac thuc
        #Neu mot don hang nhu vay da ton tai thì sẽ lấy nó
        #Nếu không nó sẽ tạo một đơn đặt hàng mới với Plete được đặt thành false
        #Phương thức get_ỏ_create() trả về một bộ chứa đối tượng đươn hàng và một giá trị boolean cho biết đơn hàng đã được tạo hay truy xuất
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        #truy xuat tat ca cac muc trong don dat hang bang phuong thuc orderitem_set.all()
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total':0,'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order,'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    print('Action: ', action)
    print('productId: ', productId)
    
    
    customer =request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)
    
    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity +1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)
    
    orderItem.save()
    
    if orderItem.quantity <=0:
        orderItem.delete()
        
    cartItems = order.get_cart_items
    response = {'cartItems': cartItems}
    return JsonResponse('Item was added', safe = False)


# Xoá sản phẩm khi khách hàng đã đăng nhập
def remove_from_cart(request, item_id):
    item = OrderItem.objects.get(id=item_id)
    item.delete()
    return redirect('cart')

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        
        if order.shipping == True:
            ShippingAddree.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zip_code = data['shipping']['zip_code'],
                
            )
    else:
        print('User is not logged in...')
    return JsonResponse('Payment complete!', safe = False)