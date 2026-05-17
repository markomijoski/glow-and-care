"""
=============================================================================
  Glow & Care — Django Models
  E-Commerce Platform for Skincare Products
=============================================================================

  Model Groups:
    1.  User & Profile         → Profile, Address
    2.  Product Catalog        → Tag, Category, Product, ProductImage,
                                  ProductVariant
    3.  Wishlist               → Wishlist, WishlistItem
    4.  Cart System            → Cart, CartItem
    5.  Order Management       → Order, OrderItem
    6.  Engagement             → Review, Notification
    7.  Marketing              → DiscountCode, Banner, NewsletterSubscriber
    8.  Support                → ReturnRequest, FAQ
    9.  Inventory              → StockMovement

  Total: 20 models
=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from .utils import unique_slug_generator


# =============================================================================
# 1. USER & PROFILE
# =============================================================================

class Address(models.Model):
    """
    Reusable address model.
    A user can have multiple saved addresses (home, work, etc.).
    Used in both Profile (default address) and Order (shipping address).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    full_name       = models.CharField(max_length=150)
    phone           = models.CharField(max_length=30)
    street          = models.CharField(max_length=255)
    city            = models.CharField(max_length=100)
    state           = models.CharField(max_length=100)
    postal_code     = models.CharField(max_length=20)
    country         = models.CharField(max_length=100, default="North Macedonia")
    is_default      = models.BooleanField(default=False)

    class Meta:
        verbose_name        = "Address"
        verbose_name_plural = "Addresses"
        ordering            = ["-is_default", "full_name"]

    def __str__(self):
        return f"{self.full_name} — {self.street}, {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        """
        Ensure only one address per user is marked as default.
        When this address is set as default, demote all others.
        """
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        super().save(*args, **kwargs)


class Profile(models.Model):
    """
    Extended user information.
    One-to-one with Django's built-in User model.
    """
    user            = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar          = models.ImageField(
        upload_to="profiles/avatars/",
        blank=True,
        null=True,
    )
    phone_number    = models.CharField(max_length=30, blank=True)
    default_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_default",
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile of {self.user.get_full_name() or self.user.username}"


# =============================================================================
# 2. PRODUCT CATALOG
# =============================================================================

class Tag(models.Model):
    """
    Flat tags for products.
    Examples: 'vegan', 'SPF', 'alcohol-free', 'for sensitive skin'.
    """
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        verbose_name        = "Tag"
        verbose_name_plural = "Tags"
        ordering            = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Hierarchical product categories using a self-referential FK.
    Example: Skincare > Moisturizers > Night Creams
    """
    name        = models.CharField(max_length=120)
    slug        = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent      = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        verbose_name        = "Category"
        verbose_name_plural = "Categories"
        ordering            = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} › {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Core product model for skincare items.
    Supports variants (size/type) via the ProductVariant model.
    Tags allow multi-attribute filtering.
    """
    name        = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=220, unique=True, blank=True)
    sku         = models.CharField(
        max_length=80,
        unique=True,
        help_text="Stock Keeping Unit — unique product identifier.",
    )
    category    = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    description = models.TextField(blank=True)
    price       = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    image       = models.ImageField(
        upload_to="products/main/",
        blank=True,
        null=True,
        help_text="Primary product image. Additional images go in ProductImage.",
    )
    stock       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True, db_index=True)  # FIXED: Phase 2 Fix 9 - Added db_index
    tags        = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="products",
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Product"
        verbose_name_plural = "Products"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self) -> bool:
        """Returns True if product has stock available."""
        return self.stock > 0

    @property
    def is_low_stock(self) -> bool:
        """Returns True if stock is low (e.g. less than 5 units)."""
        return 0 < self.stock < 5

    @property
    def primary_image(self):
        """
        Returns the primary ProductImage if set,
        otherwise falls back to the main image field.
        """
        primary = self.images.filter(is_primary=True).first()
        return primary.image if primary else self.image

    # FIXED: Phase 2 Fix 12 - Extract review eligibility check into model method
    def can_user_review(self, user):
        """
        FIXED (Phase 2 Fix 12): Centralized review eligibility check.
        
        Extracts duplicated eligibility logic that was spread across product_detail_view
        and other places. Returns clear tuple with eligibility and reason message.
        
        Review is only eligible if:
        1. User is authenticated
        2. User hasn't already reviewed this product
        3. User has a verified purchase (delivered order)
        4. Order status is DELIVERED
        
        Args:
            user: Django User instance to check
        
        Returns:
            Tuple[bool, str]: (is_eligible, reason_message)
        
        Example:
            is_eligible, reason = product.can_user_review(request.user)
            if not is_eligible:
                context['review_error'] = reason
        """
        if not user.is_authenticated:
            return False, "Sign in to review this product."
        
        # Check if user already reviewed this product
        if self.reviews.filter(user=user).exists():
            return False, "You already reviewed this product."
        
        # Check for verified purchase
        from .models import OrderItem, Order
        order_item = OrderItem.objects.filter(
            product=self,
            order__user=user
        ).first()
        
        if not order_item:
            return False, "Verified purchase required. You must have ordered this product."
        
        # Check if order is delivered
        order = order_item.order
        if order.status != Order.Status.DELIVERED:
            return False, f"Order must be delivered to review. Current status: {order.get_status_display()}."
        
        return True, "Eligible"


class ProductImage(models.Model):
    """
    Additional product images (front, back, texture, lifestyle shots).
    One product can have many images.
    """
    product     = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image       = models.ImageField(upload_to="products/gallery/")
    alt_text    = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alt text for accessibility and SEO.",
    )
    is_primary  = models.BooleanField(
        default=False,
        help_text="Mark as the primary display image.",
    )
    order       = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order (lower = shown first).",
    )

    class Meta:
        verbose_name        = "Product Image"
        verbose_name_plural = "Product Images"
        ordering            = ["order", "id"]

    def __str__(self):
        return f"Image for {self.product.name} (#{self.order})"

    def save(self, *args, **kwargs):
        """Ensure only one image per product is marked primary."""
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Variants of a product (e.g. size: 30ml / 50ml / 100ml,
    or formula: oily skin / dry skin edition).
    Each variant has its own stock and optionally overrides the base price.
    """
    product         = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name            = models.CharField(
        max_length=100,
        help_text="e.g. '50ml', 'Dry Skin Formula', 'Travel Size'",
    )
    sku             = models.CharField(max_length=80, unique=True)
    price_override  = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Leave blank to use the parent product price.",
    )
    stock           = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name        = "Product Variant"
        verbose_name_plural = "Product Variants"
        ordering            = ["product", "name"]
        unique_together     = [("product", "name")]

    def __str__(self):
        return f"{self.product.name} — {self.name}"

    def clean(self):
        """
        FIXED: Validate that variant stock doesn't exceed product stock.
        This prevents stock inconsistency where variant stock > product stock.
        Called by model admin and full_clean().
        """
        if self.stock > self.product.stock:
            raise ValidationError(
                f"Variant stock ({self.stock}) cannot exceed product stock ({self.product.stock}). "
                f"Please increase the product stock or decrease this variant's stock."
            )

    @property
    def effective_price(self):
        """Returns override price if set, else the parent product price."""
        return self.price_override if self.price_override is not None else self.product.price

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0


# =============================================================================
# 3. WISHLIST
# =============================================================================

class Wishlist(models.Model):
    """
    Each authenticated user has one wishlist.
    Created automatically on first use (e.g. via signal or get_or_create).
    """
    user        = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Wishlist"
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"Wishlist of {self.user.username}"


class WishlistItem(models.Model):
    """
    A product saved to a user's wishlist.
    Unique constraint prevents duplicate entries.
    """
    wishlist    = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product     = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
    )
    added_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        ordering            = ["-added_at"]
        unique_together     = [("wishlist", "product")]

    def __str__(self):
        return f"{self.product.name} in {self.wishlist}"


# =============================================================================
# 4. CART SYSTEM
# =============================================================================

class Cart(models.Model):
    """
    Shopping cart.
    Supports both authenticated users (via FK) and guest sessions
    (via session_key). Exactly one of user / session_key should be set.
    """
    user        = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
        db_index=True,  # FIXED: Phase 2 Fix 9 - Added db_index for faster user cart lookups
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,  # FIXED: Phase 2 Fix 9 - Added db_index for faster guest cart lookups
        help_text="Django session key for unauthenticated (guest) carts.",
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Cart"
        verbose_name_plural = "Carts"
        ordering            = ["-updated_at"]

    def __str__(self):
        owner = self.user.username if self.user else f"Guest ({self.session_key})"
        return f"Cart of {owner}"

    @property
    def total_price(self):
        """Aggregate subtotal of all items in the cart."""
        return sum(item.subtotal for item in self.cart_items.all())

    @property
    def item_count(self) -> int:
        """Total number of product units in the cart."""
        return sum(item.quantity for item in self.cart_items.all())


class CartItem(models.Model):
    """
    A single line in a cart — links a product (and optional variant)
    with a quantity.
    """
    cart        = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product     = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    variant     = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity    = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name        = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together     = [("cart", "product", "variant")]

    def __str__(self):
        variant_label = f" ({self.variant.name})" if self.variant else ""
        return f"{self.quantity}× {self.product.name}{variant_label}"

    @property
    def unit_price(self):
        """Resolves the correct price based on variant or base product."""
        return self.variant.effective_price if self.variant else self.product.price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


# =============================================================================
# 5. ORDER MANAGEMENT
# =============================================================================

class DiscountCode(models.Model):
    """
    Promotional discount codes.
    Supports percentage-based discounts, usage limits, and expiry dates.
    """
    code                = models.CharField(max_length=50, unique=True)
    discount_percent    = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage discount (0–100).",
    )
    active              = models.BooleanField(default=True)
    valid_until         = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank for no expiry.",
    )
    max_uses            = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this code can be used. Leave blank for unlimited.",
    )
    times_used          = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name        = "Discount Code"
        verbose_name_plural = "Discount Codes"
        ordering            = ["-active", "code"]

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

    @property
    def is_valid(self) -> bool:
        """
        Returns True if the code is active, not expired,
        and has not exceeded its usage limit.
        """
        if not self.active:
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False
        return True


class Order(models.Model):
    """
    A confirmed customer order.
    Stores a snapshot of the shipping address and totals at time of purchase.
    Discount codes can be applied and are tracked here.
    """

    class Status(models.TextChoices):
        PENDING     = "pending",    "Pending"
        SHIPPED     = "shipped",    "Shipped"
        DELIVERED   = "delivered",  "Delivered"
        CANCELED    = "canceled",   "Canceled"

    user                = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )
    status              = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,  # FIXED: Phase 2 Fix 9 - Added db_index for filtering by status
    )
    shipping_address    = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )
    discount_code       = models.ForeignKey(
        DiscountCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    total_price         = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Stored total at checkout. Use calculate_total() to recompute.",
    )
    notes               = models.TextField(
        blank=True,
        help_text="Delivery instructions or special requests from the customer.",
    )
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Order"
        verbose_name_plural = "Orders"
        ordering            = ["-created_at"]

    def __str__(self):
        user_label = self.user.username if self.user else "Deleted User"
        return f"Order #{self.pk} by {user_label} — {self.get_status_display()}"

    def calculate_total(self):
        """
        Recomputes the order total from its items,
        applying the discount code if present and valid.
        Saves the result to total_price.
        """
        raw_total = sum(item.subtotal for item in self.order_items.all())
        if self.discount_code and self.discount_code.is_valid:
            discount = raw_total * (self.discount_code.discount_percent / 100)
            raw_total -= discount
        self.total_price = max(raw_total, 0)
        self.save(update_fields=["total_price"])
        return self.total_price


class OrderItem(models.Model):
    """
    A snapshot of one product line at the time of purchase.
    Price is stored independently from the current product price
    to preserve historical accuracy.
    """
    order       = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    product     = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    variant     = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    price       = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price at the time of purchase (historical snapshot).",
    )
    quantity    = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name        = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        variant_label = f" ({self.variant.name})" if self.variant else ""
        return f"{self.quantity}× {product_name}{variant_label} @ {self.price}"

    @property
    def subtotal(self):
        return self.price * self.quantity


# =============================================================================
# 6. ENGAGEMENT
# =============================================================================

class Review(models.Model):
    """
    Customer review for a product.
    One review per user per product (unique_together).
    Reviews require admin approval before being shown publicly.
    """
    product     = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user        = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating      = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (worst) to 5 (best).",
    )
    comment     = models.TextField(blank=True)
    is_approved = models.BooleanField(
        default=False,
        db_index=True,  # FIXED: Phase 2 Fix 9 - Added db_index for filtering approved reviews
        help_text="Only approved reviews are shown publicly.",
    )
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Review"
        verbose_name_plural = "Reviews"
        ordering            = ["-timestamp"]
        unique_together     = [("user", "product")]

    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.rating}★)"


class Notification(models.Model):
    """
    In-app notifications for users.
    Covers order updates, promotions, and system messages.
    """

    class NotificationType(models.TextChoices):
        ORDER   = "order",  "Order Update"
        PROMO   = "promo",  "Promotion"
        SYSTEM  = "system", "System"

    user                = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title               = models.CharField(max_length=200)
    message             = models.TextField()
    notification_type   = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    is_read             = models.BooleanField(
        default=False,
        db_index=True,  # FIXED: Phase 2 Fix 9 - Added db_index for filtering unread notifications
    )
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Notification"
        verbose_name_plural = "Notifications"
        ordering            = ["-created_at"]

    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f"[{status}] {self.user.username}: {self.title}"


# =============================================================================
# 7. MARKETING
# =============================================================================

class Banner(models.Model):
    """
    Homepage or promotional banners.
    Supports scheduled display windows and display ordering.
    """
    title       = models.CharField(max_length=200)
    subtitle    = models.CharField(max_length=300, blank=True)
    image       = models.ImageField(upload_to="banners/")
    link_url    = models.URLField(
        blank=True,
        help_text="Where the banner links to when clicked.",
    )
    is_active   = models.BooleanField(default=True)
    starts_at   = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank to start immediately.",
    )
    ends_at     = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank for no end date.",
    )
    order       = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order (lower = shown first).",
    )

    class Meta:
        verbose_name        = "Banner"
        verbose_name_plural = "Banners"
        ordering            = ["order", "title"]

    def __str__(self):
        return self.title

    @property
    def is_currently_active(self) -> bool:
        """
        Returns True if the banner is active and within its
        scheduled display window (if one is set).
        """
        if not self.is_active:
            return False
        now = timezone.now()
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True


class NewsletterSubscriber(models.Model):
    """
    Email marketing subscriber list.
    Intentionally kept simple — no User FK required (guests can subscribe).
    """
    email           = models.EmailField(unique=True)
    is_active       = models.BooleanField(default=True)
    subscribed_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering            = ["-subscribed_at"]

    def __str__(self):
        status = "active" if self.is_active else "unsubscribed"
        return f"{self.email} ({status})"


# =============================================================================
# 8. SUPPORT
# =============================================================================

class ReturnRequest(models.Model):
    """
    Customer return / refund request linked to an order.
    Admin can approve or reject and leave internal notes.
    """

    class Status(models.TextChoices):
        PENDING     = "pending",    "Pending"
        APPROVED    = "approved",   "Approved"
        REJECTED    = "rejected",   "Rejected"

    order       = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="return_requests",
    )
    user        = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="return_requests",
    )
    reason      = models.TextField(help_text="Customer's reason for the return.")
    status      = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes for admins (not shown to customer).",
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Return Request"
        verbose_name_plural = "Return Requests"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"Return for Order #{self.order.pk} — {self.get_status_display()}"


class FAQ(models.Model):
    """
    Frequently asked questions.
    Can be optionally linked to a product category for contextual help.
    """
    question    = models.CharField(max_length=300)
    answer      = models.TextField()
    category    = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs",
        help_text="Optionally scope this FAQ to a specific product category.",
    )
    order       = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order (lower = shown first).",
    )
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "FAQ"
        verbose_name_plural = "FAQs"
        ordering            = ["order", "question"]

    def __str__(self):
        return self.question[:80]


# =============================================================================
# 9. INVENTORY
# =============================================================================

class StockMovement(models.Model):
    """
    Audit log of every change to product/variant stock.
    Provides a full inventory history for reporting and debugging.
    Movement types: Restock (add), Sale (subtract), Return (add back),
    Adjustment (manual correction).
    """

    class MovementType(models.TextChoices):
        RESTOCK     = "restock",    "Restock"
        SALE        = "sale",       "Sale"
        RETURN      = "return",     "Return"
        ADJUSTMENT  = "adjustment", "Manual Adjustment"

    product         = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )
    variant         = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
        help_text="Leave blank if movement applies to the base product.",
    )
    movement_type   = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )
    quantity        = models.IntegerField(
        help_text="Positive = stock added. Negative = stock removed.",
    )
    note            = models.TextField(
        blank=True,
        help_text="Optional explanation (e.g. 'New shipment from supplier X').",
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        ordering            = ["-created_at"]

    def __str__(self):
        target = str(self.variant) if self.variant else self.product.name
        sign = "+" if self.quantity >= 0 else ""
        return f"[{self.get_movement_type_display()}] {target}: {sign}{self.quantity}"