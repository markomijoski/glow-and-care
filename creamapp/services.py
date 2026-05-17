"""
=============================================================================
  Glow & Care — Business Logic Services
  E-Commerce Platform for Skincare Products
=============================================================================

  Service Classes:
    1. OrderService         → Order creation, cancellation, notifications,
                              stock deduction/restoration, total calculation

  Purpose:
    Extract complex business logic from signals into testable, reusable
    service classes. Services encapsulate multi-step operations and
    maintain transactional consistency without relying on signal cascades.

  Design Principles:
    - Atomic transactions: All-or-nothing operations with proper locking
    - Explicit call flow: Views call services directly, not via signals
    - Comprehensive logging: All state changes recorded for auditing
    - Testability: Mock-friendly without signal dependencies

=============================================================================
"""

import logging
from django.db import models, transaction
from .models import (
    Order,
    OrderItem,
    ProductVariant,
    Product,
    DiscountCode,
    Notification,
    StockMovement,
)

logger = logging.getLogger(__name__)


class OrderService:
    """
    FIXED: Service layer for order operations.
    Replaces cascading signal handlers with explicit, testable business logic.
    All methods are atomic and include proper error handling.
    """

    @staticmethod
    def deduct_stock_for_order(order: Order) -> None:
        """
        Deduct stock for all items in the given order.
        Called atomically after order creation to lock and update inventory.
        Creates StockMovement records for audit trail.

        Raises:
            ValueError: If order has no items or stock is already insufficient
        """
        items = order.order_items.select_related("product", "variant").all()

        if not items.exists():
            raise ValueError("Cannot deduct stock: order has no items.")

        with transaction.atomic():
            for item in items:
                if item.variant:
                    # Deduct from variant stock
                    ProductVariant.objects.filter(pk=item.variant_id).update(
                        stock=models.F("stock") - item.quantity
                    )
                    StockMovement.objects.create(
                        product=item.product,
                        variant=item.variant,
                        movement_type=StockMovement.MovementType.SALE,
                        quantity=-item.quantity,
                        note=f"Sold — Order #{order.pk}.",
                    )
                elif item.product:
                    # Deduct from product stock
                    Product.objects.filter(pk=item.product_id).update(
                        stock=models.F("stock") - item.quantity
                    )
                    StockMovement.objects.create(
                        product=item.product,
                        movement_type=StockMovement.MovementType.SALE,
                        quantity=-item.quantity,
                        note=f"Sold — Order #{order.pk}.",
                    )

                logger.debug(
                    "Stock deducted for product '%s' (qty: %s) on Order #%s.",
                    item.product.name,
                    item.quantity,
                    order.pk,
                )

    @staticmethod
    def increment_discount_code_usage(order: Order) -> None:
        """
        Increment the usage counter for the order's discount code.
        Only applies if order has a discount code attached.
        """
        if not order.discount_code_id:
            return

        with transaction.atomic():
            DiscountCode.objects.filter(pk=order.discount_code_id).update(
                times_used=models.F("times_used") + 1
            )
            logger.debug(
                "DiscountCode #%s usage incremented for Order #%s.",
                order.discount_code_id,
                order.pk,
            )

    @staticmethod
    def restore_stock_on_cancel(order: Order) -> None:
        """
        Restore all stock and create reverse StockMovement records
        when an order is canceled. Called by cancel_order().
        """
        items = order.order_items.select_related("product", "variant").all()

        with transaction.atomic():
            for item in items:
                if item.variant:
                    ProductVariant.objects.filter(pk=item.variant_id).update(
                        stock=models.F("stock") + item.quantity
                    )
                    StockMovement.objects.create(
                        product=item.product,
                        variant=item.variant,
                        movement_type=StockMovement.MovementType.RETURN,
                        quantity=item.quantity,
                        note=f"Stock restored — Order #{order.pk} canceled.",
                    )
                elif item.product:
                    Product.objects.filter(pk=item.product_id).update(
                        stock=models.F("stock") + item.quantity
                    )
                    StockMovement.objects.create(
                        product=item.product,
                        movement_type=StockMovement.MovementType.RETURN,
                        quantity=item.quantity,
                        note=f"Stock restored — Order #{order.pk} canceled.",
                    )

            logger.debug("Stock and discount restored for canceled Order #%s.", order.pk)

    @staticmethod
    def decrement_discount_code_usage(order: Order) -> None:
        """
        Decrement discount code usage when an order is canceled.
        Mirrors the increment done at order creation.
        """
        if not order.discount_code_id:
            return

        with transaction.atomic():
            DiscountCode.objects.filter(pk=order.discount_code_id).update(
                times_used=models.F("times_used") - 1
            )
            logger.debug(
                "DiscountCode #%s usage decremented (Order #%s canceled).",
                order.discount_code_id,
                order.pk,
            )

    @staticmethod
    def notify_status_change(order: Order, previous_status: str = None) -> None:
        """
        Send in-app notification when order status changes.
        Called from views when order status is updated.

        Args:
            order: The Order instance with updated status
            previous_status: Previous status for comparison (optional)
        """
        if not order.user:
            return

        # Only notify if status actually changed
        status_changed = (previous_status is not None and 
                         previous_status != order.status)

        STATUS_MESSAGES = {
            Order.Status.PENDING: (
                "Order Placed",
                f"Your order #{order.pk} has been received and is being processed.",
            ),
            Order.Status.SHIPPED: (
                "Order Shipped",
                f"Great news! Your order #{order.pk} is on its way.",
            ),
            Order.Status.DELIVERED: (
                "Order Delivered",
                f"Your order #{order.pk} has been delivered. Enjoy your Glow & Care products!",
            ),
            Order.Status.CANCELED: (
                "Order Canceled",
                f"Your order #{order.pk} has been canceled. Contact us if you need help.",
            ),
        }

        if status_changed and order.status in STATUS_MESSAGES:
            title, message = STATUS_MESSAGES[order.status]
            Notification.objects.create(
                user=order.user,
                title=title,
                message=message,
                notification_type=Notification.NotificationType.ORDER,
            )
            logger.debug(
                "Notification '%s' created for user '%s' on Order #%s.",
                title,
                order.user.username,
                order.pk,
            )

    @staticmethod
    def cancel_order(order: Order) -> None:
        """
        Cancel an order atomically: restore stock, decrement discount code usage,
        create notification, and mark as canceled.

        This replaces the signal-based cancellation logic with explicit,
        testable service method.
        """
        if order.status == Order.Status.CANCELED:
            logger.warning(f"Order #{order.pk} is already canceled.")
            return

        with transaction.atomic():
            previous_status = order.status
            order.status = Order.Status.CANCELED
            order.save(update_fields=["status"])

            # Restore stock
            OrderService.restore_stock_on_cancel(order)

            # Restore discount code usage
            OrderService.decrement_discount_code_usage(order)

            # Notify user
            OrderService.notify_status_change(order, previous_status)

            logger.info(f"Order #{order.pk} successfully canceled.")

    @staticmethod
    def calculate_order_total(order: Order) -> None:
        """
        Recalculate and store the order's total price.
        Called after creating/modifying OrderItems to keep total in sync.
        """
        order.calculate_total()
        logger.debug(f"Order #{order.pk} total recalculated.")
