from django.urls import path
from .views import (
    AdminDashboardView, UserListView, SellerListView, 
    AdminProductListView, OrderListView
)

app_name = 'adminpanel'

urlpatterns = [
    path('', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('sellers/', SellerListView.as_view(), name='seller_list'),
    path('products/', AdminProductListView.as_view(), name='product_list'),
    path('orders/', OrderListView.as_view(), name='order_list'),
]
