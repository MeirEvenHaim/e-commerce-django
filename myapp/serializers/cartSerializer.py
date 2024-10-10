from django.shortcuts import get_object_or_404
from rest_framework import serializers
from myapp.Models import Cart, CartItem, Product

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all())
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart',"product_name", 'product', 'quantity']

    def validate(self, data):
        cart = data.get('cart')
        user = self.context['request'].user

        # Allow admin to add products to any cart
        if not user.is_staff:
            # Ensure the cart belongs to the client making the request
            if cart.client.user != user:
                raise serializers.ValidationError("You do not have permission to add items to this cart.")

        return data

    def create(self, validated_data):
        return CartItem.objects.create(**validated_data)
    
class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, required=False)  # Allow cart_items to be provided

    class Meta:
        model = Cart
        fields = ['id', 'client', 'created_at', 'cart_items']  # Changed 'user' to 'client'

    def create(self, validated_data):
        cart_items_data = validated_data.pop('cart_items', [])
        cart = Cart.objects.create(**validated_data)
        for cart_item_data in cart_items_data:
            CartItem.objects.create(cart=cart, **cart_item_data)
        return cart

    def update(self, instance, validated_data):
        cart_items_data = validated_data.pop('cart_items', [])

        # Update cart instance
        instance.client = validated_data.get('client', instance.client)  # Changed 'user' to 'client'
        instance.save()

        # Update or create CartItems
        existing_items = {item.product.id: item for item in instance.cart_items.all()}
        new_items = {item_data['product']: item_data for item_data in cart_items_data}

        # Delete items no longer in the cart
        for product_id, item in existing_items.items():
            if product_id not in new_items:
                item.delete()

        # Update existing items and create new items
        for product_id, item_data in new_items.items():
            if product_id in existing_items:
                item = existing_items[product_id]
                item.quantity = item_data['quantity']
                item.save()
            else:
                CartItem.objects.create(cart=instance, **item_data)

        return instance