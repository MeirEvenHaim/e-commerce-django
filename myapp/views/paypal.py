import logging
from django.shortcuts import render
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from myapp.Models import Payment, Order  # Ensure correct model import
from django.conf import settings
from rest_framework.decorators import api_view 
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail

# Set up logging
logger = logging.getLogger(__name__)

# PayPal Settings
PAYPAL_RECEIVER_EMAIL = settings.PAYPAL_RECEIVER_EMAIL  # Your PayPal account email
PAYPAL_RETURN_URL = 'http://localhost:8000/paypal/payment_done/'  # Update with your production URL
PAYPAL_CANCEL_URL = 'http://localhost:8000/paypal/payment_cancelled/'  # Update with your production URL

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_payment(request):
    """Create a PayPal payment."""
    order_id = request.data.get('order_id')  # Use request.data for API views
    try:
        order = Order.objects.get(pk=order_id)

        # Create PayPal payment form
        paypal_dict = {
            "business": PAYPAL_RECEIVER_EMAIL,
            "amount": order.total_price,
            "item_name": f"Order {order.id}",
            "invoice": str(order.id),  # Unique invoice ID
            "notify_url": request.build_absolute_uri(reverse("paypal-ipn")),  # IPN URL
            "return": PAYPAL_RETURN_URL,
            "cancel_return": PAYPAL_CANCEL_URL,
            "currency_code": "USD",
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        return Response({'form_html': form.render()}, status=status.HTTP_200_OK)  # Return form HTML in response
    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} does not exist.")
        return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def payment_done(request):
    """Handle successful payment."""
    txn_id = request.GET.get('tx')
    order_id = request.GET.get('invoice')  # Get order ID from the invoice
    try:
        order = Order.objects.get(pk=order_id)

        # Update payment status
        payment = Payment.objects.get(order=order)
        payment.complete_payment(txn_id, order.total_price)

        # Redirect to a success page or render a success template
        return render(request, 'payment_success.html', {'order': order})
    except (Order.DoesNotExist, Payment.DoesNotExist):
        logger.error(f"Payment completion error for Order ID: {order_id}")
        return render(request, 'error.html', {'message': 'Payment completion error.'})

@api_view(['GET'])
def payment_cancelled(request):
    """Handle cancelled payment."""
    return render(request, 'payment_cancelled.html')

@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    """Handle IPN notifications from PayPal."""
    ipn_obj = sender  # The IPN object
    txn_id = ipn_obj.txn_id
    order_id = ipn_obj.invoice  # Get order ID from the invoice

    logger.info(f"Received IPN: {ipn_obj}")

    try:
        order = Order.objects.get(pk=order_id)
        payment = Payment.objects.get(order=order)

        if ipn_obj.payment_status == "Completed":
            logger.info(f"Payment completed for Order ID: {order_id} with Transaction ID: {txn_id}")
            payment.complete_payment(txn_id, ipn_obj.mc_gross)  # Update the payment status to completed
            send_payment_notification(order, payment)  # Send notification to user
        elif ipn_obj.payment_status in ["Pending", "Failed", "Refunded"]:
            payment.status = ipn_obj.payment_status
            payment.save()
            logger.info(f"Payment status updated to {ipn_obj.payment_status} for Order ID: {order_id}")
        else:
            logger.error(f"Unknown payment status: {ipn_obj.payment_status} for Order ID: {order_id}")
    except (Order.DoesNotExist, Payment.DoesNotExist) as e:
        logger.error(f"Order or Payment does not exist for Order ID: {order_id}. Error: {str(e)}")
        send_admin_notification(order_id, str(e))  # Notify admin for manual intervention

def send_payment_notification(order, payment):
    """Send an email notification about the payment status."""
    subject = f"Payment Update for Order ID: {order.id}"
    message = f"Your payment for Order ID {order.id} is {payment.status}.\nTransaction ID: {payment.transaction_id}\nAmount: {payment.amount} USD."
    recipient_list = [order.user.email]  # Assuming you have a user associated with the order

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def send_admin_notification(order_id, error_message):
    """Send an email to admin if there's an issue with payment processing."""
    subject = f"Payment Processing Error for Order ID: {order_id}"
    message = f"There was an error processing payment for Order ID {order_id}.\nError: {error_message}"
    recipient_list = [settings.ADMIN_EMAIL]  # Ensure you have this setting in your settings.py

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
