# C:\Users\meire\OneDrive\Desktop\backend - supermarket-template\myapp\Models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from paypal.standard.models import ST_PP_COMPLETED  # Payment completed status
from paypal.standard.ipn.signals import valid_ipn_received  # Signal for IPN
from django.dispatch import receiver

    
# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Supplier Model
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField()

    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, related_name='Products', on_delete=models.CASCADE, db_index=True)
    supplier = models.ForeignKey(Supplier, related_name='Products', on_delete=models.CASCADE, db_index=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Handle image uploads

    def __str__(self):
           return f"{self.name} (ID: {self.id})" 


class Cart(models.Model):
    user = models.ForeignKey(User, related_name='Cart', on_delete=models.CASCADE)  # Changed 'user' to 'client'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user}"


class Cart_link_product(models.Model):
    cart = models.ForeignKey(Cart, related_name='Cart_link_product', on_delete=models.CASCADE)
    # product_id = models.BigIntegerField(max_length=1_000_000_000, default = 0)
    product = models.ForeignKey(Product, related_name='Cart_link_product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    def __str__(self):
      return f"{self.quantity} of {self.product.name} (ID: {self.product.id}) in Cart (ID: {self.cart.id})"


class Order(models.Model):
    user_id = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user_id}"

    def calculate_total_price(self):
        total = sum(item.product.price * item.quantity for item in self.cart.cart_items.all())
        self.total_price = total
        self.save()

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('Credit Card', 'Credit Card'), ('PayPal', 'PayPal')], default='PayPal')
    paypal_id = models.CharField(max_length=255, unique=True, blank=True, null=True)  # PayPal Transaction ID
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending')

    def complete_payment(self, txn_id, amount):
        """Mark payment as complete."""
        self.paypal_id = txn_id
        self.status = 'Completed'
        self.amount = amount
        self.save()

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"

 
# Shipping Model
class Shipping(models.Model):
    order_id = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    shipping_address = models.TextField()
    shipping_date = models.DateTimeField(blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_method = models.CharField(max_length=50, choices=[('Standard', 'Standard'), ('Express', 'Express')], default='Standard')
    delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipping {self.id} for Order {self.order.id}"
