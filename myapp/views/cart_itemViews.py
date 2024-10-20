from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from myapp.Models import Cart, CartItem, Client
from myapp.serializers.cartSerializer import CartItemSerializer, CartSerializer
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def Show_user_cart_and_create_user_cart(request):
    if request.method == 'GET':
        if request.user.is_staff:
            # Admin can see all cart items
            cart_items = CartItem.objects.all()
        else:
            # Regular client can only see their own cart items
            client = get_object_or_404(Client, user=request.user)
            cart_items = CartItem.objects.filter(cart__client=client)

        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            cart = serializer.validated_data['cart']
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            # Admins can add items to any cart; clients can only add to their own cart
            if cart.client.user != request.user and not request.user.is_staff:
                return Response({'error': 'You do not have permission to add items to this cart.'}, status=status.HTTP_403_FORBIDDEN)

            # Check if the cart item already exists
            existing_item = CartItem.objects.filter(cart=cart, product=product).first()
            if existing_item:
                # If it exists, update the quantity
                existing_item.quantity += quantity
                existing_item.save()
                return Response(CartItemSerializer(existing_item).data, status=status.HTTP_200_OK)

            # Create a new cart item
            cart_item = serializer.save()
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def modify_the_user_carts(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)

    # Admin can access all cart items; clients can only access their own cart items
    if cart_item.cart.client.user != request.user and not request.user.is_staff:
        return Response({'error': 'You do not have permission to access this cart item.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Pass the request context to the serializer
        serializer = CartItemSerializer(cart_item, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
