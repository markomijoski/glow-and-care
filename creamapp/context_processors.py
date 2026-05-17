"""
=============================================================================
  Glow & Care — Template Context Processors
  Injected into every template automatically (configured in settings.py).
=============================================================================
"""

import logging
from django.db import DatabaseError
from .models import Cart


logger = logging.getLogger(__name__)


def cart_context(request):
    """
    Makes `cart` and `cart_item_count` available in every template.
    Uses session caching to avoid redundant DB queries on every page load.
    
    FIXED (Phase 2 Fix 14): Added proper exception handling with logging.
    Previously caught all exceptions silently, making bugs invisible.
    Now logs specific database errors for debugging.
    """
    cart = None
    cart_item_count = request.session.get("cart_item_count")

    try:
        if request.user.is_authenticated:
            cart = (
                Cart.objects.filter(user=request.user)
                .prefetch_related("cart_items")
                .first()
            )
        elif request.session.session_key:
            cart = (
                Cart.objects.filter(session_key=request.session.session_key)
                .prefetch_related("cart_items")
                .first()
            )

        # If count is missing from session or cart was modified, re-calculate
        if cart and cart_item_count is None:
            cart_item_count = cart.item_count
            request.session["cart_item_count"] = cart_item_count
        elif not cart:
            cart_item_count = 0
            request.session["cart_item_count"] = 0

    except DatabaseError as db_err:
        # FIXED: Log database errors instead of silently failing
        logger.exception(
            f"Cart query failed for user {request.user.id if request.user.is_authenticated else 'guest'}: {db_err}"
        )
        cart = None
        cart_item_count = 0
    except Exception as e:
        # FIXED: Log unexpected errors for visibility
        logger.exception(f"Unexpected error in cart_context: {e}")
        cart = None
        cart_item_count = 0

    return {
        "cart": cart,
        "cart_item_count": cart_item_count or 0,
    }
