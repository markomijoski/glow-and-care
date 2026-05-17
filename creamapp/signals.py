"""
=============================================================================
  Glow & Care — Django Signals
  E-Commerce Platform for Skincare Products
=============================================================================

  Signal Groups:
    1.  User & Profile         → Auto-create Profile + Wishlist on User creation
    2.  Order Management       → Auto-calculate total on OrderItem save/delete
                                  Auto-increment DiscountCode usage on Order save
                                  Auto-create Notification on Order status change
    3.  Inventory              → Auto-create StockMovement on Product/Variant
                                  stock change
                                  Auto-deduct stock when an Order is placed
                                  Auto-restore stock when an Order is canceled
    4.  Reviews                → Auto-create Notification when a review is approved
    5.  Cart Cleanup           → Auto-delete guest carts older than 7 days on
                                  new cart creation (lightweight housekeeping)

  Registration:
    Add to your app's AppConfig.ready():

        # yourapp/apps.py
        class YourAppConfig(AppConfig):
            name = "yourapp"

            def ready(self):
                import yourapp.signals  # noqa: F401

=============================================================================
"""

import logging

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    Address,
    Banner,
    Cart,
    CartItem,
    DiscountCode,
    FAQ,
    NewsletterSubscriber,
    Notification,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductVariant,
    Profile,
    ReturnRequest,
    Review,
    StockMovement,
    Tag,
    WishlistItem,
    Wishlist,
)

logger = logging.getLogger(__name__)


def _merge_cart_items(source_cart, target_cart):
    """Merge cart items from source_cart into target_cart."""
    for source_item in source_cart.cart_items.select_related("product", "variant"):
        # Determine available stock for capping
        available_stock = source_item.variant.stock if source_item.variant else source_item.product.stock
        
        target_item, created = target_cart.cart_items.get_or_create(
            product=source_item.product,
            variant=source_item.variant,
            defaults={"quantity": min(source_item.quantity, available_stock)},
        )
        if not created:
            # Cap the new total quantity to available stock
            new_qty = target_item.quantity + source_item.quantity
            target_item.quantity = min(new_qty, available_stock)
            target_item.save(update_fields=["quantity"])


@receiver(user_logged_in)
def merge_guest_cart_on_login(sender, request, user, **kwargs):
    """Merge the remembered guest cart into the authenticated user's cart."""
    guest_session_key = request.session.get("guest_cart_session_key")
    if not guest_session_key:
        return

    guest_cart = (
        Cart.objects.filter(session_key=guest_session_key, user__isnull=True)
        .order_by("-updated_at")
        .first()
    )
    if not guest_cart:
        request.session.pop("guest_cart_session_key", None)
        return

    with transaction.atomic():
        user_cart, _ = Cart.objects.get_or_create(user=user, defaults={"session_key": None})
        if user_cart.session_key:
            user_cart.session_key = None
            user_cart.save(update_fields=["session_key"])
        _merge_cart_items(guest_cart, user_cart)
        guest_cart.delete()
        request.session["cart_item_count"] = user_cart.item_count

    request.session.pop("guest_cart_session_key", None)


# =============================================================================
# 1. USER & PROFILE
# =============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile whenever a new User is registered.
    """
    if created:
        Profile.objects.create(user=instance)
        logger.debug("Profile created for user '%s'.", instance.username)


@receiver(post_save, sender=User)
def create_user_wishlist(sender, instance, created, **kwargs):
    """
    Automatically create a Wishlist whenever a new User is registered.
    """
    if created:
        Wishlist.objects.create(user=instance)
        logger.debug("Wishlist created for user '%s'.", instance.username)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Keep the Profile in sync whenever the User is saved.
    Guards against cases where Profile was created outside of the signal
    (e.g. data migrations, fixtures).
    """
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(post_delete, sender=Address)
def promote_new_default_address_on_delete(sender, instance, **kwargs):
    """
    If the deleted address was the user's default, automatically promote
     the next most recent address to default. Prevents 'empty default' profiles.
    """
    if not instance.is_default:
        return

    next_address = Address.objects.filter(user=instance.user).order_by("-id").first()
    if next_address:
        next_address.is_default = True
        next_address.save(update_fields=["is_default"])
        logger.debug(
            "Address #%s promoted to default for user '%s' after deletion.",
            next_address.pk,
            instance.user.username,
        )


# =============================================================================
# 2. ORDER MANAGEMENT
# =============================================================================

@receiver(post_save, sender=OrderItem)
def recalculate_order_total_on_item_save(sender, instance, **kwargs):
    """
    DEPRECATED: Order total calculation now handled by OrderService.calculate_order_total()
    called explicitly from views. This signal is disabled to avoid duplicate calculations.
    Kept for reference only.
    
    Recompute and store the Order total every time an OrderItem is saved.
    Keeps total_price always consistent without manual calls.
    """
    # DISABLED: Replaced by OrderService.calculate_order_total() in views
    pass


@receiver(post_delete, sender=OrderItem)
def recalculate_order_total_on_item_delete(sender, instance, **kwargs):
    """
    DEPRECATED: Order total calculation now handled by OrderService.
    This signal is disabled to avoid duplicate calculations.
    Kept for reference only.
    
    Recompute the Order total when an OrderItem is removed.
    """
    # DISABLED: Replaced by OrderService.calculate_order_total() in views
    pass


@receiver(pre_save, sender=Order)
def cache_previous_order_status(sender, instance, **kwargs):
    """
    Before saving an Order, stash the current DB status on the instance
    so post_save signals can detect status transitions.
    """
    if instance.pk:
        try:
            instance._previous_status = Order.objects.get(pk=instance.pk).status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def increment_discount_code_usage(sender, instance, created, **kwargs):
    """
    DEPRECATED: Discount code usage now handled by OrderService.increment_discount_code_usage()
    called explicitly from views. This signal is disabled to avoid duplicate increments.
    Kept for reference only.
    
    When a new Order is created with a discount code, increment times_used atomically.
    """
    # DISABLED: Replaced by OrderService.increment_discount_code_usage() in views
    pass


@receiver(post_save, sender=Order)
def decrement_discount_code_usage(sender, instance, created, **kwargs):
    """
    DEPRECATED: Discount code restoration now handled by OrderService.decrement_discount_code_usage()
    called from OrderService.cancel_order(). This signal is disabled.
    Kept for reference only.
    
    When an Order is canceled, release the discount code usage spot.
    """
    # DISABLED: Replaced by OrderService.decrement_discount_code_usage() in cancel flow
    pass


@receiver(post_save, sender=Order)
def notify_user_on_order_status_change(sender, instance, created, **kwargs):
    """
    DEPRECATED: Order notifications now handled by OrderService.notify_status_change()
    called explicitly from views. This signal is disabled to ensure single notification point.
    Kept for reference only.
    
    Send an in-app Notification to the customer when:
      - A new order is placed (created=True)
      - The order status changes (e.g. Pending → Shipped)
    """
    # DISABLED: Replaced by OrderService.notify_status_change() in views
    pass


@receiver(post_save, sender=Order)
def restore_stock_on_order_cancel(sender, instance, **kwargs):
    """
    DEPRECATED: Stock restoration now handled by OrderService.cancel_order()
    called explicitly from cancel views or admin actions. This signal is disabled
    to ensure all cancellation logic flows through the service layer.
    Kept for reference only.
    
    When an Order is canceled, restore stock for all its items
    and create StockMovement records for the audit trail.
    Only fires on a status transition TO 'canceled'.
    """
    # DISABLED: Replaced by OrderService.cancel_order() for explicit, testable cancellation
    pass


# =============================================================================
# 3. INVENTORY — STOCK DEDUCTION ON ORDER PLACEMENT
# =============================================================================

@receiver(post_save, sender=OrderItem)
def deduct_stock_on_order_item_create(sender, instance, created, **kwargs):
    """
    DEPRECATED: Stock deduction now handled by OrderService.deduct_stock_for_order()
    called after order creation. This signal is disabled to ensure all inventory
    operations flow through the service layer with proper locking and atomicity.
    Kept for reference only.
    
    When a new OrderItem is created (i.e. an order is placed),
    deduct the quantity from the relevant Product or ProductVariant stock
    and record a StockMovement for the audit trail.

    Note: Stock restoration on cancellation is handled by
    restore_stock_on_order_cancel above.
    """
    # DISABLED: Replaced by OrderService.deduct_stock_for_order() in order_confirm_view
    pass


# =============================================================================
# 4. REVIEWS
# =============================================================================

@receiver(post_save, sender=Review)
def notify_user_on_review_approved(sender, instance, **kwargs):
    """
    Send an in-app Notification when a review transitions
    from unapproved → approved.
    Uses a cached _was_approved flag set by pre_save.
    """
    was_approved = getattr(instance, "_was_approved", None)

    # Only fire if approval status just flipped to True.
    if instance.is_approved and was_approved is False:
        Notification.objects.create(
            user=instance.user,
            title="Your Review Was Published",
            message=(
                f"Your review for '{instance.product.name}' has been approved "
                f"and is now live on the site."
            ),
            notification_type=Notification.NotificationType.SYSTEM,
        )
        logger.debug(
            "Review approval notification sent to '%s' for product '%s'.",
            instance.user.username,
            instance.product.name,
        )


@receiver(pre_save, sender=Review)
def cache_review_approval_status(sender, instance, **kwargs):
    """
    Before saving a Review, cache whether it was already approved
    so post_save can detect the approval transition.
    """
    if instance.pk:
        try:
            instance._was_approved = Review.objects.get(pk=instance.pk).is_approved
        except Review.DoesNotExist:
            instance._was_approved = False
    else:
        instance._was_approved = False  # New reviews are never pre-approved.


# =============================================================================
# 5. RETURN REQUESTS
# =============================================================================

@receiver(post_save, sender=ReturnRequest)
def notify_user_on_return_request_update(sender, instance, created, **kwargs):
    """
    Notify the customer when:
      - Their return request is submitted (created)
      - Its status changes (Pending → Approved / Rejected)
    """
    if not instance.user:
        return

    if created:
        Notification.objects.create(
            user=instance.user,
            title="Return Request Received",
            message=(
                f"We've received your return request for Order #{instance.order_id}. "
                f"Our team will review it shortly."
            ),
            notification_type=Notification.NotificationType.ORDER,
        )
        return

    previous = getattr(instance, "_previous_return_status", None)
    if previous and previous != instance.status:
        STATUS_MESSAGES = {
            ReturnRequest.Status.APPROVED: (
                "Return Request Approved",
                f"Your return request for Order #{instance.order_id} has been approved.",
            ),
            ReturnRequest.Status.REJECTED: (
                "Return Request Rejected",
                f"Your return request for Order #{instance.order_id} was not approved. "
                f"Please contact us for more details.",
            ),
        }
        if instance.status in STATUS_MESSAGES:
            title, message = STATUS_MESSAGES[instance.status]
            Notification.objects.create(
                user=instance.user,
                title=title,
                message=message,
                notification_type=Notification.NotificationType.ORDER,
            )


@receiver(pre_save, sender=ReturnRequest)
def cache_return_request_status(sender, instance, **kwargs):
    """
    Cache the current DB status before saving so post_save
    can detect status transitions.
    """
    if instance.pk:
        try:
            instance._previous_return_status = ReturnRequest.objects.get(
                pk=instance.pk
            ).status
        except ReturnRequest.DoesNotExist:
            instance._previous_return_status = None
    else:
        instance._previous_return_status = None


# =============================================================================
# 6. CART CLEANUP — LIGHTWEIGHT GUEST CART HOUSEKEEPING
# =============================================================================

@receiver(post_save, sender=Cart)
def cleanup_expired_guest_carts(sender, instance, created, **kwargs):
    """
    When a new Cart is created, delete guest carts (no user) older than 7 days.
    This is a lightweight, zero-dependency alternative to a Celery beat task.
    It runs in the background of normal usage rather than on a schedule.

    For high-traffic sites, replace this with a scheduled management command
    or a Celery periodic task.
    """
    if not created:
        return

    expiry_threshold = timezone.now() - timezone.timedelta(days=7)
    deleted_count, _ = Cart.objects.filter(
        user__isnull=True,
        updated_at__lt=expiry_threshold,
    ).delete()

    if deleted_count:
        logger.info(
            "Cleaned up %d expired guest cart(s) older than 7 days.",
            deleted_count,
        )


# =============================================================================
# 7. PRODUCT — PRIMARY IMAGE INTEGRITY
# =============================================================================

@receiver(post_delete, sender=ProductImage)
def reassign_primary_image_on_delete(sender, instance, **kwargs):
    """
    If the deleted image was the primary one, automatically promote
    the next available image (lowest order) to primary.
    Prevents a product from having no primary image after a deletion.
    """
    if not instance.is_primary:
        return

    next_image = (
        instance.product.images.order_by("order", "id").first()
    )
    if next_image:
        next_image.is_primary = True
        next_image.save(update_fields=["is_primary"])
        logger.debug(
            "Primary image reassigned to image #%s for product '%s'.",
            next_image.pk,
            instance.product.name,
        )
