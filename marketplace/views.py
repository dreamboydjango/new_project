from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, View, DeleteView
from django.contrib import messages
from django.db import transaction
from .models import Product, Category, CartItem, Wishlist, Order, OrderItem

class ProductListView(ListView):
    model = Product
    template_name = 'marketplace/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('q')
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(category__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        return queryset.select_related('category', 'seller')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'marketplace/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.select_related('category', 'seller').filter(
            category=self.object.category, 
            is_active=True
        ).exclude(id=self.object.id)[:4]
        return context

# --- Cart Views ---

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('marketplace:cart_detail')

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'marketplace/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect('marketplace:cart_detail')

# --- Wishlist Views ---

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f"{product.name} added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
        
    return redirect('marketplace:wishlist_detail')

@login_required
def wishlist_detail(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'marketplace/wishlist_detail.html', {
        'wishlist_items': wishlist_items
    })

@login_required
def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    messages.success(request, "Item removed from your wishlist.")
    return redirect('marketplace:wishlist_detail')

# --- Order Views ---

@login_required
@transaction.atomic
def place_order(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('marketplace:cart_detail')
            
        # Create Order
        order = Order.objects.create(buyer=request.user)
        
        for item in cart_items:
            # Check stock
            if item.product.stock < item.quantity:
                messages.error(request, f"Sorry, {item.product.name} is out of stock or insufficient quantity.")
                transaction.set_rollback(True)
                return redirect('marketplace:cart_detail')
            
            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            
            # Update stock
            item.product.stock -= item.quantity
            item.product.save()
            
        # Clear Cart
        cart_items.delete()
        
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('dashboard:buyer_dashboard')
        
    return redirect('marketplace:cart_detail')
