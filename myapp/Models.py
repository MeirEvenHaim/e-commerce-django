# C:\Users\meire\OneDrive\Desktop\backend - supermarket-template\myapp\Models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from paypal.standard.models import ST_PP_COMPLETED  # Payment completed status
from paypal.standard.ipn.signals import valid_ipn_received  # Signal for IPN
from django.dispatch import receiver


class Client(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')  # New role field
    additional_info = models.TextField(blank=True, null=True)  # Example field for client-specific data

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['user__username']  # Order clients by username

    def __str__(self):
        return self.user.username

    def has_additional_info(self):
        """
        Return True if additional_info is not empty.
        """
        return bool(self.additional_info)
    
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
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, db_index=True)
    supplier = models.ForeignKey(Supplier, related_name='products', on_delete=models.CASCADE, db_index=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Handle image uploads

    def __str__(self):
           return f"{self.name} (ID: {self.id})" 


class Cart(models.Model):
    client = models.ForeignKey(Client, related_name='carts', on_delete=models.CASCADE)  # Changed 'user' to 'client'
    products = models.ManyToManyField(Product, through='CartItem')  # Many-to-Many via CartItem
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.client.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
      return f"{self.quantity} of {self.product.name} (ID: {self.product.id}) in Cart (ID: {self.cart.id})"


class Order(models.Model):
    client = models.ForeignKey(Client, related_name='orders', on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.client.username}"

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
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    shipping_address = models.TextField()
    shipping_date = models.DateTimeField(blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_method = models.CharField(max_length=50, choices=[('Standard', 'Standard'), ('Express', 'Express')], default='Standard')
    delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipping {self.id} for Order {self.order.id}"
