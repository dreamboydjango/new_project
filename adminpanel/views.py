from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from marketplace.models import Product, Order, Category
from accounts.models import User
from django.db.models import Sum

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensures the requesting user is an administrator or superuser."""

    def test_func(self):
        return self.request.user.role == 'ADMIN' or self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('accounts:login')


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'adminpanel/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['total_sellers'] = User.objects.filter(role='SELLER').count()
        context['total_products'] = Product.objects.count()
        context['total_orders'] = Order.objects.count()
        context['total_categories'] = Category.objects.count()
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        return context

class AdminBaseListView(AdminRequiredMixin, ListView):
    """Shared list view providing admin permission checking."""

class UserListView(AdminBaseListView):
    model = User
    template_name = 'adminpanel/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

class SellerListView(AdminBaseListView):
    model = User
    template_name = 'adminpanel/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.filter(role='SELLER').order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Active Sellers'
        return context

class AdminProductListView(AdminBaseListView):
    model = Product
    template_name = 'adminpanel/product_list.html'
    context_object_name = 'products_list'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.select_related('seller', 'category').all().order_by('-created_at')

class OrderListView(AdminBaseListView):
    model = Order
    template_name = 'adminpanel/order_list.html'
    context_object_name = 'orders_list'
    paginate_by = 10

    def get_queryset(self):
        # include calculated total (price * quantity) so template can display it
        from django.db.models import F, DecimalField, ExpressionWrapper

        total_expr = ExpressionWrapper(
            F('items__price') * F('items__quantity'), output_field=DecimalField()
        )
        return (
            Order.objects.select_related('buyer')
            .annotate(total_price=Sum(total_expr))
            .order_by('-created_at')
        )


# -------- Category management views --------

class CategoryListView(AdminBaseListView):
    model = Category
    template_name = 'adminpanel/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.all().order_by('name')


class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'adminpanel/category_form.html'
    success_url = reverse_lazy('adminpanel:category_list')


class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'adminpanel/category_form.html'
    success_url = reverse_lazy('adminpanel:category_list')


class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'adminpanel/category_confirm_delete.html'
    success_url = reverse_lazy('adminpanel:category_list')
