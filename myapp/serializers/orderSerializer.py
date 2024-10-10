from rest_framework import serializers
from myapp.Models import Order, Cart, Client
from myapp.serializers.cartSerializer import CartSerializer  # Keep using your existing CartSerializer

class OrderSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all())  # Just reference the cart by ID
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'client', 'cart', 'total_price', 'order_date']

    def get_total_price(self, obj):
        return obj.total_price

    def create(self, validated_data):
        # The cart should already exist, so we just use it to create the order
        order = Order.objects.create(**validated_data)
        order.calculate_total_price()  # Calculate total price after the order is created
        return order
