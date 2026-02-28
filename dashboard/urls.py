from django.urls import path
from .views import (
    SellerDashboardView, BuyerDashboardView, ProductCreateView, 
    SellerProductListView, ProductUpdateView, ProductDeleteView,
    OrderDetailView
)

app_name = 'dashboard'

urlpatterns = [
    path('seller/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('buyer/', BuyerDashboardView.as_view(), name='buyer_dashboard'),
    path('product/add/', ProductCreateView.as_view(), name='add_product'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='edit_product'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='delete_product'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('seller/products/', SellerProductListView.as_view(), name='seller_products'),
]
