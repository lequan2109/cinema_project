# Đường dẫn: cinema_app/vnpay_helpers.py (FILE MỚI)

import hashlib
import hmac
import urllib.parse
from django.conf import settings
from django.utils import timezone
import urllib.parse

def get_vnpay_payment_url(request, booking_code, total_price):
    tmn_code = settings.VNPAY_TMN_CODE
    hash_secret = settings.VNPAY_HASH_SECRET
    vnp_url = settings.VNPAY_URL
    return_url = request.build_absolute_uri(settings.VNPAY_RETURN_URL)

    order_id = booking_code
    amount = int(total_price * 100) 
    order_desc = f"Thanh toan ve xem phim cho don hang {order_id}"
    bank_code = '' 
    language = 'vn'
    ipaddr = get_client_ip(request)
    create_date = timezone.now().strftime('%Y%m%d%H%M%S')
    
    input_data = {
        'vnp_Version': '2.1.0',
        'vnp_TmnCode': tmn_code,
        'vnp_Amount': amount,
        'vnp_Command': 'pay',
        'vnp_CreateDate': create_date,
        'vnp_CurrCode': 'VND',
        'vnp_IpAddr': ipaddr,
        'vnp_Locale': language,
        'vnp_OrderInfo': order_desc,
        'vnp_OrderType': 'other',
        'vnp_ReturnUrl': return_url,
        'vnp_TxnRef': order_id,
    }

    if bank_code:
        input_data['vnp_BankCode'] = bank_code

    sorted_input_data = sorted(input_data.items())
    query_string = urllib.parse.urlencode(sorted_input_data)
    
    signature = hmac.new(
        hash_secret.encode(), 
        query_string.encode(), 
        hashlib.sha512
    ).hexdigest()

    final_url = f"{vnp_url}?{query_string}&vnp_SecureHash={signature}"
    return final_url

def verify_vnpay_return(request_data):
    hash_secret = settings.VNPAY_HASH_SECRET
    if 'vnp_SecureHash' not in request_data:
        return False, "Thiếu vnp_SecureHash"
    vnp_secure_hash = request_data['vnp_SecureHash']
    input_params = {k: v for k, v in request_data.items() if k != 'vnp_SecureHash'}
    sorted_input_data = sorted(input_params.items())
    query_string = urllib.parse.urlencode(sorted_input_data)
    new_signature = hmac.new(
        hash_secret.encode(), 
        query_string.encode(), 
        hashlib.sha512
    ).hexdigest()
    
    if new_signature == vnp_secure_hash:
        if request_data.get('vnp_ResponseCode') == '00':
            return True, "Thanh toán thành công"
        else:
            return False, f"Lỗi VNPAY: {request_data.get('vnp_TransactionStatus', 'Lỗi không xác định')}"
    else:
        return False, "Chữ ký không hợp lệ"

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip