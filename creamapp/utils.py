import string
import random
from django.utils.text import slugify
from django.db.models import F


def random_string_generator(size=4, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    Generates a unique slug for a model instance.
    If the slug already exists, appends a random string and tries again.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        # We assume the model has a 'name' field. 
        # Fallback to 'title' if 'name' doesn't exist.
        source_text = getattr(instance, 'name', getattr(instance, 'title', 'item'))
        slug = slugify(source_text)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    
    if qs_exists:
        new_slug = f"{slug}-{random_string_generator(size=4)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


# ============================================================================
# PHASE 2 FIX 7: STOCK VALIDATION UTILITY
# ============================================================================
# FIXED: Extract repeated stock validation logic into a reusable function.
# This is called from cart_add_view, cart_update_view, and product detail.
# ============================================================================

def validate_stock(product, variant, requested_qty):
    """
    FIXED (Phase 2 Fix 7): Validates if the requested quantity is available.
    
    Extracts the stock validation logic that was repeated 3+ times across views.
    DRY principle: Single source of truth for stock limits.
    
    Args:
        product: Product instance
        variant: ProductVariant instance (or None for base product)
        requested_qty: Integer quantity being requested
    
    Returns:
        Tuple[bool, str | None, int]
        - is_valid: Whether the quantity is available
        - error_message: Human-readable error (None if valid)
        - available_stock: Number of items in stock
    
    Example:
        is_valid, error_msg, avail = validate_stock(product, variant, 5)
        if not is_valid:
            return JsonResponse({"error": error_msg, "available": avail}, status=400)
    """
    # Determine which stock to check (variant takes precedence)
    available = variant.stock if variant else product.stock
    
    # Cap quantity at 999 to prevent database issues
    requested_qty = min(int(requested_qty), 999)
    
    # Validate requested quantity doesn't exceed available stock
    if requested_qty > available:
        return False, f"Only {available} in stock.", available
    
    if requested_qty < 1:
        return False, "Quantity must be at least 1.", available
    
    return True, None, available


# ============================================================================
# PHASE 2 FIX 8: CART RETRIEVAL HELPER
# ============================================================================
# FIXED: Extract boilerplate cart get_or_create logic used in 5+ places.
# Centralizes cart retrieval with proper prefetch_related.
# ============================================================================

def get_or_create_user_cart(request):
    """
    FIXED (Phase 2 Fix 8): Centralized cart retrieval for authenticated/guest users.
    
    Replaces 5+ instances of cart lookup boilerplate in views and context processors.
    Handles both authenticated users (cart.user) and guest sessions (cart.session_key).
    Includes optimized prefetch_related for common views.
    
    Args:
        request: Django request object with user and session
    
    Returns:
        Cart instance (or creates if doesn't exist)
    
    Example:
        cart = get_or_create_user_cart(request)
        # vs. old way:
        # if request.user.is_authenticated:
        #     cart = Cart.objects.get_or_create(user=request.user)[0]
        # else:
        #     if not request.session.session_key:
        #         request.session.create()
        #     cart = Cart.objects.get_or_create(session_key=request.session.session_key)[0]
    """
    from .models import Cart
    
    if request.user.is_authenticated:
        cart, _ = Cart.objects.select_related(
            'user'
        ).prefetch_related(
            'cart_items__product__images',
            'cart_items__variant'
        ).get_or_create(user=request.user)
    else:
        # Ensure session exists before retrieving guest cart
        if not request.session.session_key:
            request.session.create()
        
        cart, _ = Cart.objects.select_related(
            'user'
        ).prefetch_related(
            'cart_items__product__images',
            'cart_items__variant'
        ).get_or_create(session_key=request.session.session_key)
    
    return cart
