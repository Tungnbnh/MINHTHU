from django.shortcuts import render, get_object_or_404

from django.http import JsonResponse,HttpResponseNotFound
from .models import *
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

import json
from . utils import cookieCart, cartData, guestOrder
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from xhtml2pdf import pisa
# Create your views here.

def store(request):
    category_id = request.GET.get('category')
    if category_id:
        category = Category.objects.get(id=category_id)
        products = Product.objects.filter(category=category_id)
        
        
    else:
        category = None
        
        products = Product.objects.all()
    
     
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
       

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

# def product_detail(request):
#     context = {}
#     return render(request, 'store/product_detail.html', context)
def detail(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    product = get_object_or_404(Product, pk=pk)
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'product': product}
    return render(request, 'store/detail.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

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
def remove_from_cart_guest(request, item_id):
    guest_cart = request.session.get('guest_cart', {})
    if item_id in guest_cart:
        del guest_cart[item_id]
        request.session['guest_cart'] = guest_cart
    return redirect('cart')


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
         
    else:
        customer, order = guestOrder(request, data)
        
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
    return JsonResponse('Payment complete!', safe = False)


# def view_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id) # thay pk thành id
#     order_items = OrderItem.objects.filter(order=order)
#     products = Product.objects.all()

#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         product = get_object_or_404(Product, id=product_id)

#         # Kiểm tra xem OrderItem đã tồn tại hay chưa
#         order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

#         # Nếu đã tồn tại, cập nhật số lượng sản phẩm thêm vào
#         if not created:
#             order_item.quantity += 1
#             order_item.save()

#         # Nếu chưa tồn tại, tạo một OrderItem mới với số lượng sản phẩm là 1
#         else:
#             new_order_item = OrderItem(order=order, product=product, quantity=1)
#             new_order_item.save()

#     # Truy vấn thông tin sản phẩm trong đơn hàng
#     order_items = order.orderitem_set.all()

#     context = {
#         'order': order,
#         'order_items': order_items,
#         'products': products,   
#     }
#     return render(request, 'store/view_order.html', context)
def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # order_items = OrderItem.get_order_items_by_order(order_id)
    order_items = OrderItem.get_order_items_by_order(order).order_by('-date_added')
    # Truy vấn thông tin khách hàng và địa chỉ giao hàng
    customer = order.customer
    shipping_addresses = order.get_shipping_addresses()

    context = {
        'order': order,
        'order_items': order_items,
        'customer': customer,
        'shipping_addresses': shipping_addresses,
    }

    return render(request, 'store/view_order.html', context)

def view_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # order_items = OrderItem.get_order_items_by_order(order_id)
    order_items = OrderItem.get_order_items_by_order(order).order_by('-date_added')
    # Truy vấn thông tin khách hàng và địa chỉ giao hàng
    customer = order.customer
    shipping_addresses = order.get_shipping_addresses()

    context = {
        'order': order,
        'order_items': order_items,
        'customer': customer,
        'shipping_addresses': shipping_addresses,
    }

    return render(request, 'store/view_order_detail.html', context)


