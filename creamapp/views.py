import json
import logging
import uuid
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Avg, Case, Count, IntegerField, Q, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from .forms import AddressForm, UserForm, ProfileForm
from .models import (
	Address,
	Cart,
	CartItem,
	Category,
	DiscountCode,
	Banner,
	FAQ,
	NewsletterSubscriber,
	Order,
	OrderItem,
	Product,
	ProductVariant,
	Profile,
	Review,
	Tag,
	Wishlist,
	WishlistItem,
)
from .services import OrderService
from .utils import validate_stock, get_or_create_user_cart  # FIXED: Phase 2 Fixes 7 & 8

logger = logging.getLogger(__name__)


CATALOG_SORT_OPTIONS = {
	"newest": "Newest",
	"price_asc": "Price: Low to High",
	"top_rated": "Top Rated",
}


def _get_descendant_category_ids(root_category):
	"""Return all descendant category ids using breadth-first traversal."""
	ids = [root_category.id]
	queue = [root_category.id]
	while queue:
		children = list(
			Category.objects.filter(parent_id__in=queue).values_list("id", flat=True)
		)
		if not children:
			break
		ids.extend(children)
		queue = children
	return ids


def _annotate_product_metrics(queryset):
	"""Annotate products with rating and review aggregates for cards and sorting."""
	approved_reviews = Q(reviews__is_approved=True)
	queryset = queryset.annotate(
		avg_rating=Avg("reviews__rating", filter=approved_reviews),
		review_count=Count("reviews", filter=approved_reviews, distinct=True),
	)
	return queryset.annotate(
		has_no_rating=Case(
			When(avg_rating__isnull=True, then=1),
			default=0,
			output_field=IntegerField(),
		)
	)


class CatalogQueryMixin:
	"""Shared filtering and sorting logic for product discovery surfaces."""

	def get_base_queryset(self):
		queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("tags", "images")
		return _annotate_product_metrics(queryset)

	def _parse_decimal(self, key):
		value = (self.request.GET.get(key) or "").strip()
		if not value:
			return None
		try:
			parsed = Decimal(value)
		except (InvalidOperation, ValueError):
			return None
		return max(parsed, Decimal("0"))

	def apply_filters(self, queryset, *, enforce_category=None):
		# Multi-category support
		category_slugs = [s.strip() for s in self.request.GET.getlist("category") if s.strip()]
		if enforce_category:
			category_slugs = [enforce_category.slug]
		
		# Multi-tag support
		tag_slugs = [s.strip() for s in self.request.GET.getlist("tag") if s.strip()]
		
		min_price = self._parse_decimal("min_price")
		max_price = self._parse_decimal("max_price")
		min_rating = (self.request.GET.get("min_rating") or "").strip()
		in_stock_only = (self.request.GET.get("in_stock") == "true")

		# User Request: Min price must be below max price
		if min_price is not None and max_price is not None:
			if min_price > max_price:
				min_price, max_price = max_price, min_price # Auto-swap for robustness

		selected_categories = []
		if category_slugs:
			selected_categories = list(Category.objects.filter(slug__in=category_slugs))
			all_cat_ids = []
			for cat in selected_categories:
				all_cat_ids.extend(_get_descendant_category_ids(cat))
			queryset = queryset.filter(category_id__in=list(set(all_cat_ids)))

		if tag_slugs:
			queryset = queryset.filter(tags__slug__in=tag_slugs)

		if min_price is not None:
			queryset = queryset.filter(price__gte=min_price)
		if max_price is not None:
			queryset = queryset.filter(price__lte=max_price)
			
		if min_rating and min_rating.isdigit():
			queryset = queryset.filter(avg_rating__gte=int(min_rating))
			
		if in_stock_only:
			queryset = queryset.filter(is_in_stock=True)

		sort = (self.request.GET.get("sort") or "newest").strip()
		if sort == "price_asc":
			queryset = queryset.order_by("price", "name")
		elif sort == "price_desc":
			queryset = queryset.order_by("-price", "name")
		elif sort == "top_rated":
			queryset = queryset.order_by("has_no_rating", "-avg_rating", "-review_count", "-created_at")
		else:
			sort = "newest"
			queryset = queryset.order_by("-created_at")

		return queryset.distinct(), {
			"selected_categories": selected_categories,
			"selected_category_slugs": category_slugs,
			"selected_tag_slugs": tag_slugs,
			"selected_sort": sort,
			"selected_min_price": min_price,
			"selected_max_price": max_price,
			"selected_min_rating": int(min_rating) if min_rating.isdigit() else None,
			"in_stock_only": in_stock_only,
		}

	def get_catalog_context(self):
		# Annotate categories with product counts
		active_products = Q(products__is_active=True)
		categories = Category.objects.annotate(
			product_count=Count("products", filter=active_products, distinct=True)
		).select_related("parent").order_by("name")

		tags = Tag.objects.annotate(
			product_count=Count("products", filter=active_products, distinct=True)
		).order_by("name")

		# Add price desc to options
		full_sort_options = CATALOG_SORT_OPTIONS.copy()
		full_sort_options["price_desc"] = "Price: High to Low"

		return {
			"categories": categories,
			"tags": tags,
			"sort_options": full_sort_options,
			"star_range": [5, 4, 3, 2, 1], # Reverse for UI
		}


class ProductListView(CatalogQueryMixin, ListView):
	template_name = "creamapp/product_list.html"
	context_object_name = "products"
	paginate_by = 12

	def get_queryset(self):
		queryset, state = self.apply_filters(self.get_base_queryset())
		self.catalog_state = state
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.get_catalog_context())
		context.update(self.catalog_state)
		return context


class SearchView(CatalogQueryMixin, ListView):
	template_name = "creamapp/search_results.html"
	context_object_name = "products"
	paginate_by = 12

	def get_queryset(self):
		query = (self.request.GET.get("q") or "").strip()
		queryset = self.get_base_queryset()
		if query:
			queryset = queryset.filter(
				Q(name__icontains=query)
				| Q(description__icontains=query)
				| Q(tags__name__icontains=query)
			)
		queryset, state = self.apply_filters(queryset)
		self.catalog_state = state
		self.search_query = query
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.get_catalog_context())
		context.update(self.catalog_state)
		context["query"] = self.search_query
		return context


class CategoryDetailView(CatalogQueryMixin, ListView):
	template_name = "creamapp/category_detail.html"
	context_object_name = "products"
	paginate_by = 12

	def dispatch(self, request, *args, **kwargs):
		self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		queryset, state = self.apply_filters(
			self.get_base_queryset(),
			enforce_category=self.category,
		)
		self.catalog_state = state
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.get_catalog_context())
		context.update(self.catalog_state)
		context["category"] = self.category
		context["subcategory_list"] = self.category.subcategories.order_by("name")
		return context


class ProductDetailView(DetailView):
	template_name = "creamapp/product_detail.html"
	context_object_name = "product"

	def get_queryset(self):
		return (
			Product.objects.filter(is_active=True)
			.select_related("category")
			.prefetch_related("tags", "images", "variants", "reviews__user")
		)

	def get_object(self, queryset=None):
		queryset = queryset or self.get_queryset()
		return get_object_or_404(queryset, slug=self.kwargs["slug"])

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		product = self.object

		# --- Recently Viewed Logic ---
		recent = self.request.session.get('recently_viewed', [])
		if product.id in recent:
			recent.remove(product.id)
		recent.insert(0, product.id)
		self.request.session['recently_viewed'] = recent[:6] 
		self.request.session.modified = True

		# Exclude current and fetch others
		recent_ids = [pid for pid in recent if pid != product.id]
		context['recently_viewed_products'] = Product.objects.filter(
			id__in=recent_ids, is_active=True
		).prefetch_related('images')[:4]

		gallery_images = product.images.order_by("order", "id")
		variants = product.variants.order_by("name")
		approved_reviews = product.reviews.filter(is_approved=True).select_related("user")
		review_stats = approved_reviews.aggregate(avg_rating=Avg("rating"), review_count=Count("id"))

		distribution = approved_reviews.values('rating').annotate(count=Count('id'))
		star_counts = {i: 0 for i in range(1, 6)}
		for d in distribution:
			star_counts[d['rating']] = d['count']
		
		total_reviews = review_stats.get("review_count", 0)
		star_distribution = []
		for star in range(5, 0, -1):
			count = star_counts[star]
			pct = (count / total_reviews * 100) if total_reviews > 0 else 0
			star_distribution.append({
				'star': star,
				'count': count,
				'percent': pct
			})

		can_review = False
		if self.request.user.is_authenticated:
			has_ordered = OrderItem.objects.filter(
				order__user=self.request.user,
				order__status__in=[Order.Status.DELIVERED],
				product=product
			).exists()
			has_reviewed = Review.objects.filter(user=self.request.user, product=product).exists()
			can_review = has_ordered and not has_reviewed

		selected_variant = None
		selected_variant_id = (self.request.GET.get("variant") or "").strip()
		if selected_variant_id.isdigit():
			selected_variant = variants.filter(pk=int(selected_variant_id)).first()
		if selected_variant is None:
			selected_variant = variants.first()

		display_price = selected_variant.effective_price if selected_variant else product.price
		variant_data = [
			{
				"id": variant.id,
				"price": str(variant.effective_price),
				"in_stock": variant.is_in_stock,
			}
			for variant in variants
		]

		related_products = (
			_annotate_product_metrics(
				Product.objects.filter(is_active=True, category=product.category)
				.exclude(pk=product.pk)
				.select_related("category")
			)
			.order_by("-created_at")[:4]
		)

		context.update(
			{
				"gallery_images": gallery_images,
				"variants": variants,
				"selected_variant": selected_variant,
				"display_price": display_price,
				"variant_data": variant_data,
				"approved_reviews": approved_reviews,
				"avg_rating": review_stats.get("avg_rating"),
				"review_count": review_stats.get("review_count", 0),
				"star_distribution": star_distribution,
				"can_review": can_review,
				"related_products": related_products,
				"star_range": [1, 2, 3, 4, 5],
			}
		)
		return context


def home_view(request):
	banners = Banner.objects.filter(is_active=True).order_by("order")
	featured_categories = Category.objects.filter(parent__isnull=True)[:4]
	
	base_qs = _annotate_product_metrics(Product.objects.filter(is_active=True).prefetch_related("images"))
	best_sellers = base_qs.annotate(order_count=Count("order_items")).order_by("-order_count")[:8]
	new_arrivals = base_qs.order_by("-created_at")[:8]
	
	promo = DiscountCode.objects.filter(active=True).first()
	reviews = Review.objects.filter(is_approved=True).select_related("user", "product").order_by("-timestamp")[:6]
	
	context = {
		"banners": banners,
		"featured_categories": featured_categories,
		"best_sellers": best_sellers,
		"new_arrivals": new_arrivals,
		"promo": promo,
		"reviews": reviews,
		"star_range": [1, 2, 3, 4, 5],
	}
	return render(request, "creamapp/home.html", context)


def newsletter_subscribe_view(request):
	if request.method == "POST":
		email = request.POST.get("email", "").strip()
		if not email:
			import json
			try:
				data = json.loads(request.body)
				email = data.get("email", "").strip()
			except:
				pass
				
		if email:
			from .models import NewsletterSubscriber
			NewsletterSubscriber.objects.get_or_create(email=email)
			return JsonResponse({"success": True, "message": "Thanks for subscribing!"})
			
	return JsonResponse({"success": False, "error": "Invalid email."}, status=400)


def login_view(request):
	return redirect("account_login")


def register_view(request):
	return redirect("account_signup")


def password_reset_view(request):
	return redirect("account_reset_password")


def logout_view(request):
	return redirect("account_logout")


@login_required
def profile_view(request):
	profile, _ = Profile.objects.get_or_create(user=request.user)
	if request.method == "POST":
		user_form = UserForm(request.POST, instance=request.user)
		profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, "Your profile has been updated successfully.")
			return redirect("profile")
	else:
		user_form = UserForm(instance=request.user)
		profile_form = ProfileForm(instance=profile)

	return render(request, "creamapp/profile.html", {
		"profile": profile,
		"user_form": user_form,
		"profile_form": profile_form
	})


search_view = SearchView.as_view()
product_list_view = ProductListView.as_view()
product_detail_view = ProductDetailView.as_view()
category_detail_view = CategoryDetailView.as_view()

@login_required
def review_create_view(request, slug):
	if request.method != "POST":
		return redirect("product_detail", slug=slug)
		
	product = get_object_or_404(Product, slug=slug, is_active=True)
	
	has_ordered = OrderItem.objects.filter(
		order__user=request.user,
		order__status__in=[Order.Status.DELIVERED],
		product=product
	).exists()
	
	has_reviewed = Review.objects.filter(user=request.user, product=product).exists()
	
	if not has_ordered:
		messages.error(request, "You can only review products you have purchased and received.")
		return redirect("product_detail", slug=slug)
		
	if has_reviewed:
		messages.error(request, "You have already submitted a review for this product.")
		return redirect("product_detail", slug=slug)
		
	rating = request.POST.get("rating")
	comment = request.POST.get("comment", "").strip()
	
	if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
		messages.error(request, "Please select a valid star rating.")
		return redirect("product_detail", slug=slug)
		
	Review.objects.create(
		user=request.user,
		product=product,
		rating=int(rating),
		comment=comment,
		is_approved=False
	)
	
	messages.success(request, "Thank you! Your review has been submitted and is pending approval.")
	return redirect("product_detail", slug=slug)


@login_required
def notifications_view(request):
	notifications = request.user.notifications.all()[:50]
	return render(
		request,
		"creamapp/notifications.html",
		{"notifications": notifications},
	)


@login_required
def notification_mark_read_view(request, pk):
	if request.method == "POST":
		from .models import Notification
		try:
			notif = Notification.objects.get(pk=pk, user=request.user)
			notif.is_read = True
			notif.save(update_fields=["is_read"])
			return JsonResponse({"success": True})
		except Notification.DoesNotExist:
			return JsonResponse({"error": "Not found"}, status=404)
	return JsonResponse({"error": "POST required"}, status=405)


@login_required
def notification_mark_all_read_view(request):
	if request.method == "POST":
		request.user.notifications.filter(is_read=False).update(is_read=True)
		return JsonResponse({"success": True})
	return JsonResponse({"error": "POST required"}, status=405)


@login_required
def wishlist_view(request):
	wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
	items = wishlist.items.select_related("product").all()
	return render(
		request,
		"creamapp/wishlist.html",
		{"wishlist": wishlist, "items": items},
	)


@login_required
def wishlist_add_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)

	payload = _parse_json_body(request)
	product = get_object_or_404(Product, pk=payload.get("product_id"), is_active=True)
	wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
	WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

	if request.content_type and "application/json" in request.content_type:
		return JsonResponse({"message": "Added to wishlist"})

	messages.success(request, "Added to wishlist.")
	return redirect(request.META.get("HTTP_REFERER") or "wishlist")


@login_required
def wishlist_remove_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)

	payload = _parse_json_body(request)
	product_id = payload.get("product_id")
	
	try:
		wishlist = Wishlist.objects.get(user=request.user)
		item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
		item.delete()
		
		if request.content_type and "application/json" in request.content_type:
			return JsonResponse({"removed": True})
			
		messages.success(request, "Removed from wishlist.")
	except (Wishlist.DoesNotExist, WishlistItem.DoesNotExist):
		pass
		
	return redirect(request.META.get("HTTP_REFERER") or "wishlist")


@login_required
def order_list_view(request):
	orders = request.user.orders.select_related("shipping_address", "discount_code").all()
	return render(
		request,
		"creamapp/order_list.html",
		{"orders": orders},
	)


@login_required
def address_list_view(request):
	addresses = request.user.addresses.all()
	return render(
		request,
		"creamapp/address_list.html",
		{"addresses": addresses},
	)


def faq_view(request):
	faqs = FAQ.objects.filter(is_active=True).select_related("category").order_by("order", "question")
	return render(
		request,
		"creamapp/faq.html",
		{"faqs": faqs},
	)


def _parse_json_body(request):
	if request.content_type and "application/json" in request.content_type:
		try:
			return json.loads(request.body.decode("utf-8") or "{}")
		except (json.JSONDecodeError, UnicodeDecodeError):
			return {}
	return request.POST


def _update_cart_session_count(request, cart):
	"""Internal helper to sync cart count with session for performance."""
	if cart:
		count = cart.item_count
		request.session["cart_item_count"] = count
		return count
	request.session["cart_item_count"] = 0
	return 0


def cart_add_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)

	payload = _parse_json_body(request)
	product_id = payload.get("product_id")
	variant_id = payload.get("variant_id")
	quantity = payload.get("quantity", 1)

	try:
		quantity = max(int(quantity), 1)
	except (TypeError, ValueError):
		quantity = 1

	product = get_object_or_404(Product, pk=product_id, is_active=True)
	variant = None
	if variant_id:
		variant = get_object_or_404(ProductVariant, pk=variant_id, product=product)

	# FIXED: Use get_or_create_user_cart() helper (Phase 2 Fix 8)
	cart = get_or_create_user_cart(request)

	# ─── Critical Section: Stock validation + update under lock ────────────
	# FIXED: Uses select_for_update() to prevent race condition
	# Ensures another request cannot modify cart between check and add
	try:
		with transaction.atomic():
			# Lock the existing cart item (if any) to prevent concurrent modifications
			existing_item = cart.cart_items.select_for_update().filter(
				product=product,
				variant=variant
			).first()
			
			existing_qty = existing_item.quantity if existing_item else 0
			total_qty = existing_qty + quantity
			
			# FIXED: Use validate_stock() utility (Phase 2 Fix 7)
			is_valid, error_msg, available_stock = validate_stock(product, variant, total_qty)
			if not is_valid:
				return JsonResponse({
					"success": False,
					"error": error_msg,
					"available_stock": available_stock,
					"cart_item_count": cart.item_count,
				}, status=400)

			# Now safe to add: both item and stock are locked
			item, created = CartItem.objects.get_or_create(
				cart=cart,
				product=product,
				variant=variant,
				defaults={"quantity": quantity},
			)
			if not created:
				item.quantity += quantity
				item.save(update_fields=["quantity"])

	except CartItem.DoesNotExist:
		return JsonResponse({"error": "Error updating cart"}, status=500)

	cart.refresh_from_db()
	count = _update_cart_session_count(request, cart)

	return JsonResponse({
		"message": "Added to cart",
		"cart_item_count": count,
		"success": True,
	})


def cart_detail_view(request):
	# FIXED: Use get_or_create_user_cart() helper (Phase 2 Fix 8)
	cart = get_or_create_user_cart(request)

	cart_items = cart.cart_items.select_related("product", "variant").prefetch_related("product__images")
	return render(
		request,
		"creamapp/cart_detail.html",
		{"cart": cart, "cart_items": cart_items},
	)


def _get_current_cart(request):
	"""Return the cart for the current user or guest session, or None."""
	if request.user.is_authenticated:
		return Cart.objects.filter(user=request.user).prefetch_related("cart_items").first()
	if request.session.session_key:
		return Cart.objects.filter(session_key=request.session.session_key).prefetch_related("cart_items").first()
	return None


def cart_update_view(request, item_id):
	"""
	POST /cart/update/<item_id>/
	Payload: { quantity: int }  (JSON or form-data)
	Returns updated line subtotal and cart totals as JSON.
	Validates that the item belongs to the current user/session cart.
	FIXED: Uses select_for_update() to prevent race condition
	"""
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)

	cart = _get_current_cart(request)
	if not cart:
		return JsonResponse({"error": "Cart not found"}, status=404)

	payload = _parse_json_body(request)
	try:
		quantity = int(payload.get("quantity", 1))
	except (TypeError, ValueError):
		return JsonResponse({"error": "Invalid quantity"}, status=400)

	quantity = max(1, quantity)

	# ─── Critical Section: Stock validation + update under lock ────────────
	try:
		with transaction.atomic():
			# Lock the cart item to prevent concurrent modifications
			item = cart.cart_items.select_for_update().select_related("product").get(pk=item_id)
			
			# FIXED: Use validate_stock() utility (Phase 2 Fix 7)
			is_valid, error_msg, available_stock = validate_stock(item.product, item.variant, quantity)
			if not is_valid:
				return JsonResponse({
					"success": False,
					"error": error_msg,
					"available_stock": available_stock,
					"current_quantity": item.quantity,
				}, status=400)

			# Now safe to update: item and stock are locked
			item.quantity = quantity
			item.save(update_fields=["quantity"])

	except CartItem.DoesNotExist:
		return JsonResponse({"error": "Item not found"}, status=404)

	cart.refresh_from_db()
	count = _update_cart_session_count(request, cart)

	return JsonResponse({
		"item_id": item.pk,
		"quantity": item.quantity,
		"unit_price": str(item.unit_price),
		"subtotal": str(item.subtotal),
		"cart_total": str(cart.total_price),
		"cart_item_count": count,
		"success": True,
	})


def cart_remove_view(request, item_id):
	"""
	POST /cart/remove/<item_id>/
	Deletes the cart line and returns updated cart totals as JSON.
	Validates that the item belongs to the current user/session cart.
	"""
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)

	cart = _get_current_cart(request)
	if not cart:
		return JsonResponse({"error": "Cart not found"}, status=404)

	item = cart.cart_items.filter(pk=item_id).first()
	if not item:
		return JsonResponse({"error": "Item not found in your cart"}, status=404)

	item.delete()

	# Refresh cart totals after deletion
	cart.refresh_from_db()

	count = _update_cart_session_count(request, cart)

	return JsonResponse({
		"removed": True,
		"item_id": item_id,
		"cart_total": str(cart.total_price),
		"cart_item_count": count,
		"cart_empty": count == 0,
	})


# =============================================================================
# CHECKOUT
# =============================================================================

@login_required
def checkout_view(request):
	"""
	GET /checkout/
	Single-page checkout: shows address picker, discount code input,
	and a read-only order summary. Redirects to cart if cart is empty.
	FIXED: Generates one-time checkout token to prevent double-submission
	"""
	cart = Cart.objects.filter(user=request.user).prefetch_related(
		"cart_items__product__images",
		"cart_items__variant",
	).first()

	if not cart or cart.item_count == 0:
		messages.warning(request, "Your cart is empty. Add some items before checking out.")
		return redirect("cart_detail")

	cart_items = cart.cart_items.select_related("product", "variant").prefetch_related("product__images")
	saved_addresses = request.user.addresses.order_by("-is_default", "full_name")
	address_form = AddressForm()

	# ─── Generate one-time checkout token ─────────────────────────────────
	# Token is invalidated after first successful order submission
	checkout_token = str(uuid.uuid4())
	request.session["checkout_token"] = checkout_token
	request.session.modified = True

	return render(request, "creamapp/checkout.html", {
		"cart": cart,
		"cart_items": cart_items,
		"saved_addresses": saved_addresses,
		"address_form": address_form,
		"checkout_token": checkout_token,
	})


@login_required
def apply_discount_view(request):
	"""
	POST /checkout/apply-discount/
	AJAX endpoint. Validates a discount code and returns discount info as JSON.
	"""
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=405)

	payload = _parse_json_body(request)
	code_str = (payload.get("code") or "").strip().upper()

	if not code_str:
		return JsonResponse({"valid": False, "message": "Please enter a discount code."})

	discount = DiscountCode.objects.filter(code__iexact=code_str).first()

	if not discount or not discount.is_valid:
		return JsonResponse({"valid": False, "message": "This code is invalid or has expired."})

	return JsonResponse({
		"valid": True,
		"code": discount.code,
		"discount_percent": str(discount.discount_percent),
		"message": f"{discount.discount_percent}% off applied!",
	})


@login_required
def order_confirm_view(request):
	"""
	POST /checkout/confirm/
	Creates the Order + OrderItems atomically, clears the cart,
	optionally sends a confirmation email.
	"""
	if request.method != "POST":
		return redirect("checkout")

	cart = Cart.objects.filter(user=request.user).prefetch_related(
		"cart_items__product",
		"cart_items__variant",
	).first()

	# ─── Idempotency Check: One-Time Token ─────────────────────────────────
	# FIXED: Uses one-time checkout token instead of static CSRF token
	# Token is generated in checkout_view() and invalidated after first successful order
	submitted_token = request.POST.get("checkout_token", "").strip()
	session_token = request.session.get("checkout_token")

	if not submitted_token or not session_token or submitted_token != session_token:
		# Token missing or mismatch — redirect to checkout to get a new token
		messages.error(request, "Your checkout session has expired. Please try again.")
		return redirect("checkout")

	if not cart or cart.item_count == 0:
		messages.error(request, "Your cart is empty.")
		return redirect("cart_detail")

	# -- Resolve shipping address ------------------------------------------
	address_id = request.POST.get("address_id", "").strip()
	address = None

	if address_id and address_id.isdigit():
		address = get_object_or_404(Address, pk=int(address_id), user=request.user)
	else:
		# New address form submitted
		form = AddressForm(request.POST)
		if form.is_valid():
			address = form.save(commit=False)
			address.user = request.user
			address.save()
		else:
			# Re-render checkout with form errors
			saved_addresses = request.user.addresses.order_by("-is_default", "full_name")
			cart_items = cart.cart_items.select_related("product", "variant").prefetch_related("product__images")
			messages.error(request, "Please fix the address errors below.")
			return render(request, "creamapp/checkout.html", {
				"cart": cart,
				"cart_items": cart_items,
				"saved_addresses": saved_addresses,
				"address_form": form,
			})

	# -- Resolve discount code ---------------------------------------------
	discount_code = None
	code_str = (request.POST.get("discount_code") or "").strip().upper()
	if code_str:
		candidate = DiscountCode.objects.filter(code__iexact=code_str).first()
		if candidate and candidate.is_valid:
			discount_code = candidate

	# -- Notes -------------------------------------------------------------
	notes = (request.POST.get("notes") or "").strip()

	# -- Create order atomically -------------------------------------------
	try:
		with transaction.atomic():
			# 1. Lock and Verify Stock (Individual Items)
			items = cart.cart_items.select_related("product", "variant").all()
			
			for cart_item in items:
				if cart_item.variant:
					v = ProductVariant.objects.select_for_update().get(pk=cart_item.variant_id)
					if v.stock < cart_item.quantity:
						messages.error(request, f"Sorry, {cart_item.product.name} ({v.name}) only has {v.stock} left in stock.")
						raise ValueError("stock_error")
				else:
					p = Product.objects.select_for_update().get(pk=cart_item.product_id)
					if p.stock < cart_item.quantity:
						messages.error(request, f"Sorry, {cart_item.product.name} only has {p.stock} left in stock.")
						raise ValueError("stock_error")

			# FIXED: Product-Level Stock Sync Check (Fix 6)
			# Ensures that when multiple variants/base items of the same product are ordered,
			# the total doesn't exceed product-level stock allocation.
			# This prevents subtle data inconsistency where sum(variant_stock) > product_stock.
			product_quantities = {}
			for cart_item in items:
				product_id = cart_item.product_id
				if product_id not in product_quantities:
					product_quantities[product_id] = 0
				product_quantities[product_id] += cart_item.quantity
			
			for product_id, total_qty in product_quantities.items():
				product = Product.objects.select_for_update().get(pk=product_id)
				if product.stock < total_qty:
					# Re-check at order level to catch race condition where another request
					# depleted product stock after individual variant checks
					messages.error(
						request,
						f"Sorry, {product.name} doesn't have {total_qty} items available. "
						f"Only {product.stock} left in stock across all variants."
					)
					raise ValueError("stock_error_product_level")

			# 2. Create Order
			order = Order.objects.create(
				user=request.user,
				shipping_address=address,
				discount_code=discount_code,
				notes=notes,
				status=Order.Status.PENDING,
			)

			# 3. Create Order Items
			for cart_item in items:
				OrderItem.objects.create(
					order=order,
					product=cart_item.product,
					variant=cart_item.variant,
					price=cart_item.unit_price,
					quantity=cart_item.quantity,
				)

			# 4. Finalize Order (FIXED: Use OrderService for proper business logic)
			# Calculate total, deduct stock, increment discount usage, send notifications
			OrderService.calculate_order_total(order)
			OrderService.deduct_stock_for_order(order)
			OrderService.increment_discount_code_usage(order)
			OrderService.notify_status_change(order)
			
			# 5. Clear Cart
			cart.cart_items.all().delete()
			cart.delete()
			request.session["cart_item_count"] = 0
			
			# 6. Invalidate checkout token to prevent replay attacks
			# Token can only be used once
			if "checkout_token" in request.session:
				del request.session["checkout_token"]
			request.session.modified = True

	except ValueError as e:
		if str(e) in ("stock_error", "stock_error_product_level"):
			return redirect("cart_detail")
		raise e
	except Exception as exc:
		logger.exception(f"Order creation failed for user {request.user.id}: {exc}")
		messages.error(request, f"Something went wrong: {str(exc)}")
		return redirect("checkout")

	# -- Confirmation email (with proper error handling) ──────────────────────
	# FIXED: Logs email failures instead of silently ignoring
	try:
		send_mail(
			subject=f"Order #{order.pk} confirmed - Glow & Care",
			message=(
				f"Hi {request.user.get_full_name() or request.user.username},\n\n"
				f"Your order #{order.pk} has been received and is being prepared.\n"
				f"Total: ${order.total_price}\n\n"
				f"Thank you for shopping with Glow & Care!\n"
			),
			from_email=None,
			recipient_list=[request.user.email],
		)
	except Exception as email_exc:
		# Log email failure but don't fail the entire checkout
		logger.error(f"Email send failed for order {order.pk}: {email_exc}")
		# User still gets success page, but issue is logged for manual follow-up

	messages.success(request, f"Order #{order.pk} placed successfully!")
	return redirect("order_success", pk=order.pk)


@login_required
def order_success_view(request, pk):
	order = get_object_or_404(
		Order.objects.prefetch_related(
			"order_items__product__images",
			"order_items__variant",
		).select_related("shipping_address", "discount_code"),
		pk=pk,
		user=request.user,
	)
	return render(request, "creamapp/order_success.html", {"order": order})


@login_required
def order_detail_view(request, pk):
	order = get_object_or_404(
		Order.objects.prefetch_related(
			"order_items__product__images",
			"order_items__variant",
		).select_related("shipping_address", "discount_code"),
		pk=pk,
		user=request.user,
	)
	return render(request, "creamapp/order_detail.html", {"order": order})


@login_required
def order_return_view(request, pk):
	order = get_object_or_404(Order, pk=pk, user=request.user)
	if order.status not in [Order.Status.SHIPPED, Order.Status.DELIVERED]:
		messages.error(request, "This order cannot be returned yet.")
		return redirect("order_detail", pk=pk)

	if request.method == "POST":
		reason = request.POST.get("reason", "").strip()
		if reason:
			from .models import ReturnRequest
			ReturnRequest.objects.create(
				order=order,
				user=request.user,
				reason=reason
			)
			messages.success(request, "Return request submitted successfully. We will review it shortly.")
			return redirect("order_detail", pk=pk)
		else:
			messages.error(request, "Please provide a reason for your return.")

	return render(request, "creamapp/order_return.html", {"order": order})


# =============================================================================
# ADDRESS BOOK
# =============================================================================

@login_required
def address_create_view(request):
	if request.method == "POST":
		form = AddressForm(request.POST)
		if form.is_valid():
			addr = form.save(commit=False)
			addr.user = request.user
			addr.save()
			messages.success(request, "Address added successfully.")
			return redirect("address_list")
	else:
		form = AddressForm()
	return render(request, "creamapp/address_form.html", {"form": form})


@login_required
def address_edit_view(request, pk):
	addr = get_object_or_404(Address, pk=pk, user=request.user)
	if request.method == "POST":
		form = AddressForm(request.POST, instance=addr)
		if form.is_valid():
			form.save()
			messages.success(request, "Address updated successfully.")
			return redirect("address_list")
	else:
		form = AddressForm(instance=addr)
	return render(request, "creamapp/address_form.html", {"form": form, "address": addr})


@login_required
def address_delete_view(request, pk):
	if request.method == "POST":
		addr = get_object_or_404(Address, pk=pk, user=request.user)
		addr.delete()
		messages.success(request, "Address deleted.")
	return redirect("address_list")


@login_required
def address_set_default_view(request, pk):
	if request.method == "POST":
		addr = get_object_or_404(Address, pk=pk, user=request.user)
		addr.is_default = True
		addr.save()
		messages.success(request, "Default address updated.")
	return redirect("address_list")


def terms_view(request):
	return render(request, 'creamapp/terms.html')

def privacy_view(request):
	return render(request, 'creamapp/privacy.html')
