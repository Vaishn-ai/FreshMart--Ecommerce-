"""
Thin wrappers around the Razorpay and Stripe SDKs.
Both providers require real API keys in .env (RAZORPAY_KEY_ID/SECRET, STRIPE_SECRET_KEY) —
until those are set, calls raise PaymentConfigError with a clear message instead of failing silently.
"""
from decouple import config


class PaymentConfigError(Exception):
    pass


def get_razorpay_client():
    import razorpay
    key_id = config("RAZORPAY_KEY_ID", default="")
    key_secret = config("RAZORPAY_KEY_SECRET", default="")
    if not key_id or not key_secret:
        raise PaymentConfigError("Razorpay credentials are not configured. Set RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET in .env.")
    return razorpay.Client(auth=(key_id, key_secret))


def create_razorpay_order(order):
    client = get_razorpay_client()
    amount_paise = int(order.total * 100)
    rp_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": order.order_number,
        "notes": {"order_id": str(order.id)},
    })
    return rp_order


def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    client = get_razorpay_client()
    client.utility.verify_payment_signature({
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    })  # raises razorpay.errors.SignatureVerificationError on failure
    return True


def get_stripe():
    import stripe
    secret_key = config("STRIPE_SECRET_KEY", default="")
    if not secret_key:
        raise PaymentConfigError("Stripe credentials are not configured. Set STRIPE_SECRET_KEY in .env.")
    stripe.api_key = secret_key
    return stripe


def create_stripe_payment_intent(order):
    stripe = get_stripe()
    intent = stripe.PaymentIntent.create(
        amount=int(order.total * 100),
        currency="inr",
        metadata={"order_id": str(order.id), "order_number": order.order_number},
    )
    return intent


def retrieve_stripe_payment_intent(payment_intent_id):
    stripe = get_stripe()
    return stripe.PaymentIntent.retrieve(payment_intent_id)
