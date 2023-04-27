from django.contrib import admin

from .models import*
# Register your models here.
#Chi tiet danh muc trong trang admin
class ProductInline(admin.TabularInline):
    model = Product
    extra = 0

class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
#chi tiet order item trong trang admin

    

admin.site.register(Category, CategoryAdmin)
admin.site.register(Customer)
# admin.site.register(Category)
admin.site.register(Product)

class OrderAdmin(admin.ModelAdmin):
    def customer_name(self, obj):
        return obj.customer.name if obj.customer else None
    customer_name.short_description = 'Khách hàng'
    
    def date_ordered(self, obj):
        return obj.date_ordered
    date_ordered.short_description = 'Ngày đặt hàng'
    
    def detail(self, obj):
        url = reverse('view_order', args=[obj.pk])
        return format_html('<a class="button" href="{}">Xem chi tiết</a>', url)
    detail.short_description = 'Chi tiết'
    
    list_display = ['id', 'customer_name', 'date_ordered', 'detail']

admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem)
# admin.site.register(ShippingAddree)

class OrderItemDetailAdmin(admin.ModelAdmin):
    def order_id(self, obj):
        return obj.order.id
    
    def customer(self, obj):
        return obj.order.customer
    
    def date_ordered(self, obj):
        return obj.order.date_ordered
    
    def complete(self, obj):
        return obj.order.complete
    
    def transaction_id(self, obj):
        return obj.order.transaction_id
    
    list_display = ['customer', 'product', 'quantity', 'date_added', 'order_id', 'date_ordered', 'complete', 'transaction_id']
    search_fields = ['product__name']
    
admin.site.register(OrderItem, OrderItemDetailAdmin)

#Hien thi chi tiet nhung gi lien quan den dia chi don hang
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'address', 'city', 'state', 'zip_code', 'date_added')
    search_fields = ('customer__name', 'address', 'city', 'state', 'zip_code')
    list_filter = ('date_added',)
    ordering = ('-date_added',)

admin.site.register(ShippingAddree, ShippingAddressAdmin)