from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from marketplace.models import Product, Order, OrderItem
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .forms import ProductForm

class SellerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/seller_dashboard.html'

    def test_func(self):
        return self.request.user.role == 'SELLER' or self.request.user.role == 'ADMIN'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.request.user
        
        # Statistics
        products = Product.objects.filter(seller=seller)
        context['total_products'] = products.count()
        context['low_stock_products'] = products.filter(stock__lte=5).count()
        
        # Sales Analytics
        order_items = OrderItem.objects.filter(product__seller=seller)
        context['total_revenue'] = order_items.aggregate(total=Sum('price'))['total'] or 0
        context['total_orders'] = order_items.values('order').distinct().count()
        
        # Recent Orders
        context['recent_order_items'] = order_items.select_related('order', 'order__buyer', 'product').order_by('-order__created_at')[:5]
        
        # Chart Data (Sales by Month)
        sales_data = order_items.annotate(month=TruncMonth('order__created_at')) \
            .values('month').annotate(total=Sum('price')).order_by('month')
        
        context['chart_labels'] = [d['month'].strftime('%b %Y') for d in sales_data]
        context['chart_data'] = [float(d['total']) for d in sales_data]
        
        return context

class BuyerDashboardView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard/buyer_dashboard.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).prefetch_related('items').order_by('-created_at')

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'dashboard/product_form.html'
    success_url = reverse_lazy('dashboard:seller_dashboard')

    def test_func(self):
        return self.request.user.role == 'SELLER'
        
    def form_valid(self, form):
        form.instance.seller = self.request.user
        messages.success(self.request, "Product listed successfully!")
        return super().form_valid(form)

class SellerProductListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = 'dashboard/seller_product_list.html'
    context_object_name = 'products'

    def test_func(self):
        return self.request.user.role == 'SELLER'

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by('-created_at')

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'dashboard/product_form.html'
    success_url = reverse_lazy('dashboard:seller_products')

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully!")
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'dashboard/product_confirm_delete.html'

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user == product.seller or user.role == 'ADMIN' or user.is_superuser

    def get_success_url(self):
        if self.request.user.role == 'ADMIN' or self.request.user.is_superuser:
            return reverse_lazy('adminpanel:product_list')
        return reverse_lazy('dashboard:seller_products')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Product deleted successfully!")
        return super().delete(request, *args, **kwargs)

class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'dashboard/order_detail.html'
    context_object_name = 'order'

    def test_func(self):
        order = self.get_object()
        user = self.request.user
        return user == order.buyer or user.role == 'ADMIN' or user.is_superuser

    def get_queryset(self):
        return Order.objects.prefetch_related('items__product')
