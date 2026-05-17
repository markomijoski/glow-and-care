# yourapp/admin.py
from django.contrib import admin
from .models import (
    Address, Profile,
    Tag, Category, Product, ProductImage, ProductVariant,
    Wishlist, WishlistItem,
    Cart, CartItem,
    Order, OrderItem, DiscountCode,
    Review, Notification,
    Banner, NewsletterSubscriber,
    ReturnRequest, FAQ,
    StockMovement,
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ["user", "phone_number", "created_at"]
    search_fields = ["user__username", "user__email", "phone_number"]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "user", "city", "country", "is_default"]
    search_fields = ["full_name", "user__username", "city", "postal_code"]
    list_filter   = ["country", "is_default"]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ["name", "parent", "slug"]
    search_fields = ["name"]
    list_filter   = ["parent"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ["name", "sku", "category", "price", "stock", "is_active", "created_at"]
    search_fields = ["name", "sku", "description"]
    list_filter   = ["is_active", "category", "tags"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display  = ["product", "alt_text", "is_primary", "order"]
    list_filter   = ["is_primary"]
    search_fields = ["product__name", "alt_text"]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display  = ["product", "name", "sku", "effective_price", "stock"]
    search_fields = ["product__name", "name", "sku"]

    def save_model(self, request, obj, form, change):
        """
        FIXED: Call full_clean() to validate stock constraints.
        This ensures variant stock doesn't exceed product stock before saving.
        """
        obj.full_clean()
        super().save_model(request, obj, form, change)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display  = ["user", "created_at"]
    search_fields = ["user__username"]

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display  = ["wishlist", "product", "added_at"]
    search_fields = ["product__name", "wishlist__user__username"]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ["user", "session_key", "item_count", "total_price", "updated_at"]
    search_fields = ["user__username", "session_key"]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display  = ["cart", "product", "variant", "quantity", "subtotal"]
    search_fields = ["product__name", "cart__user__username"]

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display  = ["code", "discount_percent", "active", "valid_until", "times_used", "max_uses", "is_valid"]
    search_fields = ["code"]
    list_filter   = ["active"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ["id", "user", "status", "total_price", "discount_code", "created_at"]
    search_fields = ["user__username", "id"]
    list_filter   = ["status"]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ["order", "product", "variant", "price", "quantity", "subtotal"]
    search_fields = ["product__name", "order__id"]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ["user", "product", "rating", "is_approved", "timestamp"]
    search_fields = ["user__username", "product__name", "comment"]
    list_filter   = ["is_approved", "rating"]
    list_editable = ["is_approved"]
    actions       = ["approve_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        for review in queryset:
            review.is_approved = True
            review.save(update_fields=["is_approved"])

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ["user", "title", "notification_type", "is_read", "created_at"]
    search_fields = ["user__username", "title"]
    list_filter   = ["notification_type", "is_read"]

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display  = ["title", "is_active", "is_currently_active", "starts_at", "ends_at", "order"]
    list_filter   = ["is_active"]
    search_fields = ["title"]

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display  = ["email", "is_active", "subscribed_at"]
    list_filter   = ["is_active"]
    search_fields = ["email"]

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display  = ["order", "user", "status", "created_at"]
    search_fields = ["user__username", "order__id"]
    list_filter   = ["status"]

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ["question", "category", "order", "is_active"]
    list_filter   = ["is_active", "category"]
    search_fields = ["question", "answer"]

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display  = ["product", "variant", "movement_type", "quantity", "created_at"]
    list_filter   = ["movement_type"]
    search_fields = ["product__name", "note"]