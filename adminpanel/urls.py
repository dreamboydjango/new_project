from django.urls import path
from .views import (
    AdminDashboardView, UserListView, SellerListView, 
    AdminProductListView, OrderListView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView
)

app_name = 'adminpanel'

urlpatterns = [
    path('', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('sellers/', SellerListView.as_view(), name='seller_list'),
    path('products/', AdminProductListView.as_view(), name='product_list'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
]
