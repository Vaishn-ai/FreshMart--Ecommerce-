from decimal import Decimal
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from accounts.models import Address
from cart.models import Cart
from coupons.models import CouponUsage
from .models import Order, OrderItem, OrderStatusHistory

EXPRESS_SURCHARGE = Decimal("49.00")


class CheckoutError(Exception):
    pass


@transaction.atomic
def create_order_from_cart(user, address_id, shipping_method, payment_method):
    cart = Cart.objects.select_for_update().get(user=user)
    items = list(cart.items.filter(saved_for_later=False).select_related("product", "variant"))

    if not items:
        raise CheckoutError("Your cart is empty.")

    # Re-validate stock right before order creation to avoid race conditions
    for item in items:
        if item.quantity > item.available_stock:
            raise CheckoutError(f"'{item.product.name}' no longer has enough stock.")

    address = Address.objects.get(id=address_id, user=user)

    delivery_charge = cart.delivery_charge
    if shipping_method == "express":
        delivery_charge += EXPRESS_SURCHARGE

    order = Order.objects.create(
        user=user,
        shipping_name=address.full_name,
        shipping_phone=address.phone,
        shipping_line1=address.line1,
        shipping_line2=address.line2,
        shipping_city=address.city,
        shipping_state=address.state,
        shipping_pincode=address.pincode,
        shipping_country=address.country,
        shipping_method=shipping_method,
        subtotal=cart.subtotal,
        discount_amount=cart.discount_amount,
        delivery_charge=delivery_charge,
        tax_amount=cart.tax_amount,
        total=cart.subtotal - cart.discount_amount + delivery_charge + cart.tax_amount,
        coupon=cart.coupon,
        payment_method=payment_method,
        payment_status="paid" if payment_method == "cod" else "pending",
        status="confirmed" if payment_method == "cod" else "pending",
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            product_name=item.product.name,
            unit_price=item.unit_price,
            quantity=item.quantity,
        )
        # decrement stock
        if item.variant:
            item.variant.stock -= item.quantity
            item.variant.save(update_fields=["stock"])
        else:
            item.product.stock -= item.quantity
            item.product.sold_count += item.quantity
            item.product.save(update_fields=["stock", "sold_count"])
            if item.product.stock <= 10:
                try:
                    from notifications.tasks import send_low_stock_alert_email
                    send_low_stock_alert_email.delay(item.product.name, item.product.stock, item.product.sku)
                except Exception:
                    pass

    OrderStatusHistory.objects.create(order=order, status=order.status, note="Order placed")

    if cart.coupon:
        CouponUsage.objects.get_or_create(coupon=cart.coupon, user=user, order_id=order.id)
        cart.coupon.times_used += 1
        cart.coupon.save(update_fields=["times_used"])

    # Clear the cart (active items only — saved-for-later items remain)
    cart.items.filter(saved_for_later=False).delete()
    cart.coupon = None
    cart.save(update_fields=["coupon"])

    if order.payment_status == "paid":
        send_order_confirmation_email(order)

    return order


def send_order_confirmation_email(order):
    """Phase 4: real delivery happens via Celery task in notifications; this is the synchronous fallback."""
    try:
        send_mail(
            f"FreshMart — Order {order.order_number} confirmed",
            f"Thanks for your order! Your order {order.order_number} totalling ₹{order.total} has been confirmed.",
            settings.EMAIL_HOST_USER or "no-reply@freshmart.local",
            [order.user.email],
            fail_silently=True,
        )
    except Exception:
        pass


def advance_order_status(order, new_status, note=""):
    order.status = new_status
    order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(order=order, status=new_status, note=note)
    if new_status == "delivered":
        send_status_update_email(order, "Your order has been delivered! 🎉")
    elif new_status == "shipped":
        send_status_update_email(order, "Your order is on its way.")
    elif new_status == "cancelled":
        send_status_update_email(order, "Your order has been cancelled.")

    try:
        from notifications.tasks import send_order_status_sms
        send_order_status_sms.delay(str(order.id), new_status)
    except Exception:
        pass  # Celery worker not running / broker unavailable — non-fatal


def send_status_update_email(order, message):
    try:
        send_mail(
            f"FreshMart — Order {order.order_number} update",
            message,
            settings.EMAIL_HOST_USER or "no-reply@freshmart.local",
            [order.user.email],
            fail_silently=True,
        )
    except Exception:
        pass
