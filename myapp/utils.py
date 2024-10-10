import logging

logger = logging.getLogger('myapp')

def get_client_ip(request):
    """Utility function to get client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_with_context(logger, request, message, level='info'):
    """Utility function to log with contextual info."""
    user = getattr(request, 'user', None)
    if user.is_authenticated:
        user = user.username
    else:
        user = 'Anonymous'

    extra = {
        'client_ip': get_client_ip(request),
        'user': user,
        'method': request.method,
        'path': request.path,
    }

    log_method = getattr(logger, level, 'info')
    log_method(message, extra=extra)

import requests

def verify_ipn(ipn_data):
    """
    Verify the IPN data with PayPal by sending it back.
    """
    verify_url = 'https://ipnpb.paypal.com/cgi-bin/webscr'
    # Prepare the payload to send back to PayPal for validation
    verify_payload = {'cmd': '_notify-validate'}
    verify_payload.update(ipn_data)
    
    # Send a POST request to PayPal with the IPN data
    response = requests.post(verify_url, data=verify_payload)
    
    if response.status_code == 200 and response.text == 'VERIFIED':
        return True
    else:
        return False
# Inside the payment_notification function after verifying the IPN
