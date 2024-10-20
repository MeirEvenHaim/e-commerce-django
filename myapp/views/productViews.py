from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from myapp.Models import Product
from myapp.serializers.productSerializer import ProductSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

# Authenticated users can view all products, and only admins can add products
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def creation_of_products_and_preview_products(request):
    if request.method == 'GET':
        products = Product.objects.all()  # Retrieve all products
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.is_staff:  # Ensure only admins can add products
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, 
                        status=status.HTTP_403_FORBIDDEN)

# Admins can view, update, and delete specific product details
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])  # Both authenticated users and admins can access this view
def modifying_existing_products(request, pk):
    product = get_object_or_404(Product, pk=pk)  # Retrieve the product
    
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    # Only admins can update or delete products
    if not request.user.is_staff:
        return Response({"detail": "You do not have permission to perform this action."}, 
                        status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':  # Update product
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':  # Delete product
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
