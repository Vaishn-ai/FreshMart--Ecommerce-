"""
Async notification tasks. Email actually sends (via Django's EMAIL_BACKEND).
SMS is a hook — plug in Twilio/MSG91/etc. inside send_sms_notification once you have credentials;
until then it logs instead of failing the whole order flow.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, subject, message, recipient_list):
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER or "no-reply@freshmart.local", recipient_list, fail_silently=False)
    except Exception as exc:
        logger.warning("Email send failed, retrying: %s", exc)
        raise self.retry(exc=exc, countdown=30)


@shared_task
def send_sms_notification(phone_number, message):
    """
    SMS hook — no live provider wired yet. Swap this body for e.g.:
        from twilio.rest import Client
        client = Client(config("TWILIO_SID"), config("TWILIO_AUTH_TOKEN"))
        client.messages.create(to=phone_number, from_=config("TWILIO_FROM"), body=message)
    """
    logger.info("[SMS STUB] to=%s message=%s", phone_number, message)
    return {"status": "stubbed", "to": phone_number}


@shared_task
def send_order_status_sms(order_id, status_label):
    from orders.models import Order
    try:
        order = Order.objects.select_related("user").get(id=order_id)
    except Order.DoesNotExist:
        return
    send_sms_notification.delay(order.shipping_phone, f"FreshMart: your order {order.order_number} is now {status_label}.")


@shared_task
def send_low_stock_alert_email(product_name, stock, sku):
    admin_emails = [settings.EMAIL_HOST_USER] if settings.EMAIL_HOST_USER else []
    if not admin_emails:
        logger.info("[LOW STOCK] %s (%s) — %s left", product_name, sku, stock)
        return
    send_email_notification.delay(
        f"Low stock: {product_name}",
        f"'{product_name}' (SKU {sku}) has only {stock} units left.",
        admin_emails,
    )
