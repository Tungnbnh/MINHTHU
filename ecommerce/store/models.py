from django.db import models
from django.urls import reverse
from django.utils.html import format_html
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Customer(models.Model):
        user = models.OneToOneField(User, null = True, blank= True, on_delete=models.CASCADE)
        name = models.CharField(max_length=200, null = True)
        email = models.CharField(max_length= 200, null = True)
        
        def __str__(self):
            return self.name
        
    
class Category(models.Model):
    name = models.CharField(max_length=200, null = True)
    
    @staticmethod
    def get_all_categories():
        return Category.objects.all()
    
    def __str__(self):
        return self.name
    
    
    def get_products(self):
        return Product.objects.filter(category=self)
   
   
    
    
    
class Product(models.Model):
    name = models.CharField(max_length= 200, null= True)
    price = models.FloatField()
    category = models.ForeignKey(Category, null= True, on_delete=models.SET_NULL, blank= True)
    digital = models.BooleanField(default= False, null = True, blank= False)
    #Digital: xem san pham co phai la hang dien tu hay ko de co the duoc van chuyen dung cach
    #Image
    description = models.TextField(null=True, blank=True)
    
    image = models.ImageField(null=True, blank= True)
    
    
    def __str__(self):
        return self.name
    # neu ko co hinh anh duoc them vao thi co the bo qua 

    
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url   
    
    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)
  
    @staticmethod
    def get_all_products():
        return Product.objects.all()
  
    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.get_all_products()
class Order(models.Model):
    customer = models.ForeignKey(Customer, null= True, on_delete=models.SET_NULL, blank= True)
    date_ordered = models.DateTimeField(auto_now_add= True)
    complete = models.BooleanField(default= False, null = True, blank= False)#Don hang mac dinh phai la chua hoan thanh
    transaction_id = models.CharField(max_length= 200, null = True)
    
    def __str__(self):
        return str(self.id)
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        #dong nay truy xuat tat ca cac muc theo thu tu bang cach su dung pt orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        #dDòng này tính toán tổng chi phí của tất cả các mặt hàng trong đơn hàng bằng cách lặp qua từng đối tượng 
        # OrderItem trong danh sách orderitems và gọi phương thức get_total trên mỗi mặt hàng.
        # Sau đó, nó cộng tất cả các tổng số mục riêng lẻ bằng cách sử dụng hàm sum() tích hợp sẵn.
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    
    def get_shipping_addresses(self):
        shipping_addresses = ShippingAddree.objects.filter(order=self)
        return shipping_addresses
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, blank=True)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, blank=True)
    quantity = models.IntegerField(default=0, null= True, blank= False)
    date_added = models.DateTimeField(auto_now_add= True)
    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    #xem chi tiet order
    # @staticmethod
    # def get_order_items_by_order(order_id):
    #     return OrderItem.objects.filter(order_id=order_id)
    @classmethod
    def get_order_items_by_order(cls, order_id):
        order_items = cls.objects.filter(order_id=order_id)
        return order_items
    
class ShippingAddree(models.Model):
    customer = models.ForeignKey(Customer, null= True, on_delete=models.SET_NULL, blank=True)
    order = models.ForeignKey(Order, null= True, on_delete=models.SET_NULL, blank=True )
    address = models.CharField(max_length= 200, null= True)
    city = models.CharField(max_length= 200, null= True)
    state = models.CharField(max_length= 200, null= True)
    zip_code = models.CharField(max_length= 200, null= True)
    date_added = models.DateTimeField(auto_now_add= True)
    
    
    def __str__(self):
        return self.address
    def get_order_items(self):
        order_items = OrderItem.objects.filter(order=self.order)
        return order_items

