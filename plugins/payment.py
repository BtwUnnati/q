import time, requests
from config import BHARATPE_MERCHANT_ID, BHARATPE_API_KEY, PREMIUM_PRICE

BASE_URL = "https://api.bharatpe.in"

def create_payment(user_id: int):
    """Create BharatPe payment request"""
    url = f"{BASE_URL}/v1/payments/qr"
    headers = {"Authorization": f"Bearer {BHARATPE_API_KEY}"}
    data = {
        "merchantId": BHARATPE_MERCHANT_ID,
        "amount": PREMIUM_PRICE,
        "orderId": f"user_{user_id}_{int(time.time())}"
    }
    r = requests.post(url, json=data, headers=headers)
    return r.json()

def check_payment(txn_id: str, user_id: int):
    """Check payment status"""
    url = f"{BASE_URL}/v1/payments/{txn_id}"
    headers = {"Authorization": f"Bearer {BHARATPE_API_KEY}"}
    r = requests.get(url, headers=headers).json()
    return r.get("status") == "SUCCESS"
