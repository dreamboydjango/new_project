from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from marketplace.models import Product, Order, OrderItem
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from .forms import ProductForm


# common statistics util for seller pages
class SellerStatsMixin:
    def get_seller(self):
        return self.request.user

    def get_products(self):
        return Product.objects.filter(seller=self.get_seller())

    def get_order_items(self):
        return OrderItem.objects.filter(product__seller=self.get_seller())

    def get_common_context(self):
        seller = self.get_seller()
        products = self.get_products()
        order_items = self.get_order_items()
        context = {
            'total_products': products.count(),
            'low_stock_products': products.filter(stock__lte=5).count(),
            'total_revenue': order_items.aggregate(total=Sum('price'))['total'] or 0,
            'total_orders': order_items.values('order').distinct().count(),
        }
        return context


class SellerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView, SellerStatsMixin):
    template_name = 'dashboard/seller_dashboard.html'

    def test_func(self):
        return self.request.user.role in ('SELLER', 'ADMIN')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.request.user
        # reuse common stats
        context.update(self.get_common_context())

        # Recent orders (last 5 items)
        order_items = self.get_order_items()
        context['recent_order_items'] = order_items.select_related('order', 'order__buyer', 'product').order_by('-order__created_at')[:5]

        # Sales by month for chart
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


# lightweight placeholder views for additional dashboard pages
class OrdersView(LoginRequiredMixin, UserPassesTestMixin, ListView, SellerStatsMixin):
    model = Order
    template_name = 'dashboard/orders.html'
    context_object_name = 'orders'

    def test_func(self):
        return self.request.user.role in ('SELLER', 'ADMIN')

    def get_queryset(self):
        # annotate with total amount and item count for easier display
        return Order.objects.filter(items__product__seller=self.request.user) \
            .annotate(total_amount=Sum('items__price'), items_count=Count('items')) \
            .distinct().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_common_context())
        return context


class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView, SellerStatsMixin):
    template_name = 'dashboard/analytics.html'

    def test_func(self):
        return self.request.user.role in ('SELLER', 'ADMIN')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_common_context())

        order_items = self.get_order_items()
        # sales by month
        sales_data = order_items.annotate(month=TruncMonth('order__created_at')) \
            .values('month').annotate(total=Sum('price')).order_by('month')
        context['chart_labels'] = [d['month'].strftime('%b %Y') for d in sales_data]
        context['chart_data'] = [float(d['total']) for d in sales_data]

        # top products by quantity
        top_products = order_items.values('product__name').annotate(
            qty=Sum('quantity'), revenue=Sum('price')
        ).order_by('-qty')[:5]
        context['top_products'] = top_products

        # orders by status counts
        status_counts = order_items.values('order__status').annotate(count=Count('order', distinct=True))
        # prepare lists for template JS to avoid inline template loops
        context['status_counts'] = status_counts
        context['status_labels'] = [s['order__status'] for s in status_counts]
        context['status_values'] = [s['count'] for s in status_counts]
        return context


class InsightsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView, SellerStatsMixin):
    template_name = 'dashboard/insights.html'

    def test_func(self):
        return self.request.user.role in ('SELLER', 'ADMIN')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_common_context())
        products = self.get_products()
        context['low_stock_items'] = products.filter(stock__lte=5).order_by('stock')

        # revenue by category
        category_revenue = self.get_order_items().annotate(
            category=F('product__category__name')
        ).values('category').annotate(total=Sum('price')).order_by('-total')
        context['category_revenue'] = category_revenue
        return context

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
