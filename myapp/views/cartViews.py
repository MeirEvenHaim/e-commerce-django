from django.forms import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from myapp.Models import Cart, Client
from myapp.serializers.cartSerializer import CartSerializer
from myapp.permissions import IsAdminOrOwner
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.forms import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from myapp.Models import Cart, Client
from myapp.serializers.cartSerializer import CartSerializer
from myapp.permissions import IsAdminOrOwner
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  # Allow all authenticated users, including admins and clients
def Show_cart_and_create_cart(request):
    if request.method == 'GET':
        if request.user.is_staff:
            # Admins can view all carts
            carts = Cart.objects.all()
        else:
            # Clients can only view their own carts
            client = get_object_or_404(Client, user=request.user)
            carts = Cart.objects.filter(client=client)  # Use the 'client' field

        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Admins can create carts for any client
        if request.user.is_staff:
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()  # Admin can save without client restrictions
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Clients can only create carts for themselves
        else:
            client = get_object_or_404(Client, user=request.user)

            # Automatically associate the cart with the current client
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(client=client)  # Correctly associate with the client
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
        
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])  # Allow all authenticated users, including admins and clients
def Show_cart_and_modify_cart(request, pk):
    cart = get_object_or_404(Cart, pk=pk)  # Get the cart by its primary key

    if request.user.is_staff:
        # Admins can access all operations on any cart
        if request.method == 'GET':
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = CartSerializer(cart, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    else:
        # For clients, ensure they can only modify their own cart
        client = get_object_or_404(Client, user=request.user)

        if cart.client != client:  # Check if the cart belongs to the client
            raise ValidationError("You can only modify or delete your own cart.")

        # Clients can access GET, PUT, DELETE only for their own carts
        if request.method == 'GET':
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = CartSerializer(cart, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)