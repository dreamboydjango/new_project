from django.urls import path
from .views import (
    SellerDashboardView, BuyerDashboardView, ProductCreateView, 
    SellerProductListView, ProductUpdateView, ProductDeleteView,
    OrderDetailView,
    OrdersView, AnalyticsView, InsightsView,
)

app_name = 'dashboard'

urlpatterns = [
    path('seller/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('buyer/', BuyerDashboardView.as_view(), name='buyer_dashboard'),

    # dashboard subpages
    path('seller/orders/', OrdersView.as_view(), name='orders'),
    path('seller/analytics/', AnalyticsView.as_view(), name='analytics'),
    path('seller/insights/', InsightsView.as_view(), name='insights'),

    path('product/add/', ProductCreateView.as_view(), name='add_product'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='edit_product'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='delete_product'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('seller/products/', SellerProductListView.as_view(), name='seller_products'),
]
