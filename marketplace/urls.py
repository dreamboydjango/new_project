from django.urls import path
from .views import (
    ProductListView, ProductDetailView, 
    add_to_cart, cart_detail, remove_from_cart,
    add_to_wishlist, wishlist_detail, remove_from_wishlist,
    place_order
)

app_name = 'marketplace'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Cart
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('order/place/', place_order, name='place_order'),
    
    # Wishlist
    path('wishlist/', wishlist_detail, name='wishlist_detail'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
]
