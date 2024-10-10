from rest_framework import serializers
from myapp.Models import Product, Supplier, Category

class ProductSerializer(serializers.ModelSerializer):
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    supplier = serializers.ReadOnlyField(source='supplier.name')
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'supplier_id', 'category_id', 'supplier', 'category', 'image']

    def create(self, validated_data):
        supplier = validated_data.pop('supplier')
        category = validated_data.pop('category')
        product = Product.objects.create(supplier=supplier, category=category, **validated_data)
        return product

    def update(self, instance, validated_data):
        supplier = validated_data.pop('supplier', None)
        category = validated_data.pop('category', None)

        if supplier:
            instance.supplier = supplier
        if category:
            instance.category = category
        
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
