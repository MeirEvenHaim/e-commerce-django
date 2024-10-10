from rest_framework import serializers
from myapp.Models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_date', 'amount', 'payment_method', 'paypal_id', 'status']

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        return payment
