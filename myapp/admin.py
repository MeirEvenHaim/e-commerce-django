# from django.contrib import admin
# from .models import Client, Supplier, Shipping, Product, Payment, Order, Category
# from myapp.models.cart import Cart ,CartItem

# @admin.register(Client)
# class ClientAdmin(admin.ModelAdmin):
#     list_display = ('email', 'address', 'phone_number', 'role', 'image')
#     search_fields = ('email', 'role')
#     list_filter = ('role',)
#     ordering = ('email',)

# @admin.register(Supplier)
# class SupplierAdmin(admin.ModelAdmin):
#     list_display = ('name', 'contact_email', 'phone_number', 'address')
#     search_fields = ('name', 'contact_email')
#     ordering = ('name',)

# @admin.register(Shipping)
# class ShippingAdmin(admin.ModelAdmin):
#     list_display = ('order', 'shipping_address', 'shipping_date', 'tracking_number', 'shipping_method', 'delivery_date')
#     search_fields = ('order__id', 'tracking_number')
#     list_filter = ('shipping_method', 'delivery_date')
#     ordering = ('shipping_date',)

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'price', 'stock', 'supplier', 'category', 'image')
#     search_fields = ('name', 'description', 'supplier__name', 'category__name')
#     list_filter = ('supplier', 'category')
#     ordering = ('name',)

# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('order', 'payment_date', 'amount', 'payment_method', 'transaction_id', 'status')
#     search_fields = ('order__id', 'transaction_id')
#     list_filter = ('payment_method', 'status')
#     ordering = ('payment_date',)

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('user', 'cart', 'order_date', 'status')
#     search_fields = ('user__email', 'cart__id')
#     list_filter = ('status',)
#     ordering = ('order_date',)

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     search_fields = ('name',)
#     ordering = ('name',)

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('user', 'created_at')
#     search_fields = ('user__email',)
#     ordering = ('created_at',)

# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ('cart', 'product', 'quantity')
#     search_fields = ('cart__id', 'product__name')
#     ordering = ('cart', 'product')
