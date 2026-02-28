from django.views.generic import ListView
from marketplace.models import Product, Category

class HomeView(ListView):
    model = Product
    template_name = 'core/home.html'
    context_object_name = 'featured_products'
    paginate_by = 8

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
