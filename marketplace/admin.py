from django.contrib import admin
from .models import Category, Product, Order, OrderItem, CartItem, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('buyer__username',)


# other models can be registered if needed
# admin.site.register(OrderItem)
# admin.site.register(CartItem)
# admin.site.register(Wishlist)
