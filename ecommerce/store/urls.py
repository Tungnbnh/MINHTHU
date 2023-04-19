
from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
 	path('update_item/', views.updateItem, name = "update_item"),
 	path('search/', views.store, name='store_search'),
   	path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
	path('remove-from-cart-guest/<int:item_id>/', views.remove_from_cart_guest, name='remove-from-cart-guest'),
   	path('process_order/', views.processOrder, name="process_order"),
	path('product/<int:pk>/', views.detail, name='detail'),

	
]