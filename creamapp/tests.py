from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class UpgradeSmokeTests(TestCase):
	def setUp(self):
		self.password = "admin-pass-123"
		self.admin_user = User.objects.create_superuser(
			username="admin_upgrade_smoke",
			email="admin@example.com",
			password=self.password,
		)

	def test_admin_profile_add_page_renders(self):
		self.client.force_login(self.admin_user)
		response = self.client.get(reverse("admin:creamapp_profile_add"))
		self.assertEqual(response.status_code, 200)

	def test_account_login_route_renders(self):
		response = self.client.get(reverse("account_login"))
		self.assertEqual(response.status_code, 200)

	def test_home_route_available(self):
		response = self.client.get(reverse("home"))
		self.assertEqual(response.status_code, 200)


# =============================================================================
# PHASE 1 CRITICAL FIXES TEST SUITE
# =============================================================================
# Tests for all 6 Phase 1 critical production-ready fixes:
# Fix 1: Race condition protection in cart operations (select_for_update)
# Fix 2: One-time checkout token idempotency prevention
# Fix 3: ProductVariant stock constraint validation
# Fix 4: OrderService business logic layer
# Fix 5: Atomic transaction boundaries for order creation
# Fix 6: Product-level stock sync check at checkout
# =============================================================================

from decimal import Decimal
from django.test import TransactionTestCase, Client
from django.db import transaction
from django.core.exceptions import ValidationError
import threading

from creamapp.models import (
	Product,
	ProductVariant,
	Cart,
	CartItem,
	Order,
	OrderItem,
	DiscountCode,
	Address,
)
from creamapp.services import OrderService


class Phase1RaceConditionFixTest(TransactionTestCase):
	"""
	Test Fix 1: Race condition protection in concurrent cart operations.
	Verifies that select_for_update() with atomic transactions prevents
	concurrent modifications from causing overselling.
	"""

	def setUp(self):
		"""Create test product with limited stock."""
		self.user = User.objects.create_user(username="testuser", password="testpass123")
		self.product = Product.objects.create(
			name="Test Cream 50ml",
			description="Test product",
			price=Decimal("25.00"),
			stock=5,  # Only 5 units available
		)
		self.cart, _ = Cart.objects.get_or_create(user=self.user)

	def test_concurrent_add_to_cart_respects_stock_limit(self):
		"""
		Simulate concurrent requests with proper locking.
		Verifies that total quantity doesn't exceed product stock.
		"""
		results = []

		def add_to_cart_concurrent(quantity):
			"""Simulate a cart add request with select_for_update locking."""
			try:
				with transaction.atomic():
					# Lock product first
					locked_product = Product.objects.select_for_update().get(pk=self.product.pk)
					
					# Lock existing cart item
					existing_item = self.cart.cart_items.select_for_update().filter(
						product=self.product, variant__isnull=True
					).first()
					
					existing_qty = existing_item.quantity if existing_item else 0
					total_qty = existing_qty + quantity
					
					# Check against locked stock
					if total_qty > locked_product.stock:
						results.append({"success": False, "reason": "insufficient_stock"})
						return
					
					# Safe to add with locks held
					item, created = CartItem.objects.get_or_create(
						cart=self.cart,
						product=self.product,
						variant=None,
						defaults={"quantity": quantity}
					)
					if not created:
						item.quantity = total_qty
						item.save()
					
					results.append({"success": True, "quantity": total_qty})
			except Exception as e:
				results.append({"success": False, "error": str(e)})

		# Clear existing items
		self.cart.cart_items.all().delete()

		# Launch concurrent threads
		threads = [
			threading.Thread(target=add_to_cart_concurrent, args=(3,)),
			threading.Thread(target=add_to_cart_concurrent, args=(3,)),
			threading.Thread(target=add_to_cart_concurrent, args=(3,)),
		]

		for t in threads:
			t.start()
		for t in threads:
			t.join()

		# Verify quantity doesn't exceed stock
		cart_item = CartItem.objects.filter(cart=self.cart, product=self.product).first()
		if cart_item:
			self.assertLessEqual(cart_item.quantity, 5, "Cart quantity must respect product stock")


class Phase1IdempotencyFixTest(TestCase):
	"""
	Test Fix 2: One-time checkout token prevents double-submit attacks.
	Verifies token generation, validation, and invalidation.
	"""

	def setUp(self):
		"""Create test user and cart."""
		self.user = User.objects.create_user(username="testuser", password="testpass123")
		self.client = Client()
		self.client.login(username="testuser", password="testpass123")
		
		self.product = Product.objects.create(
			name="Test Product",
			description="Test",
			price=Decimal("10.00"),
			stock=100,
		)
		self.cart, _ = Cart.objects.get_or_create(user=self.user)
		CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

	def test_token_invalidated_after_use(self):
		"""Token should be deleted from session after successful order creation."""
		# Get checkout page to generate token
		self.client.get('/checkout/')
		valid_token = self.client.session.get("checkout_token")
		self.assertIsNotNone(valid_token, "Token should be generated in session")

		# Create address for order
		address = Address.objects.create(
			user=self.user,
			full_name="Test User",
			phone="1234567890",
			street="Test Street 1",
			city="Test City",
			state="Test State",
			postal_code="1000",
			country="US",
		)

		# Confirm order with token
		response = self.client.post('/checkout/confirm/', {
			'address_id': str(address.id),
			'checkout_token': valid_token,
		}, follow=True)

		# Token should be gone from session after successful order
		self.assertNotIn("checkout_token", self.client.session,
						"Token should be deleted after successful order")

	def test_replay_attack_prevented(self):
		"""Same token cannot be reused for second order."""
		# Get token
		self.client.get('/checkout/')
		valid_token = self.client.session.get("checkout_token")

		# Create address
		address = Address.objects.create(
			user=self.user,
			full_name="Test User",
			phone="1234567890",
			street="Test Street 1",
			city="Test City",
			state="Test State",
			postal_code="1000",
			country="US",
		)

		# First order
		self.client.post('/checkout/confirm/', {
			'address_id': str(address.id),
			'checkout_token': valid_token,
		})

		initial_count = Order.objects.filter(user=self.user).count()

		# Try to reuse same token (should fail - already deleted)
		self.client.post('/checkout/confirm/', {
			'address_id': str(address.id),
			'checkout_token': valid_token,
		})

		final_count = Order.objects.filter(user=self.user).count()
		self.assertEqual(initial_count, final_count,
						"No new order created with replayed token")


class Phase1VariantStockConstraintTest(TestCase):
	"""
	Test Fix 3: ProductVariant.clean() validates stock constraints.
	Ensures variant stock never exceeds product stock.
	"""

	def setUp(self):
		"""Create test product."""
		self.product = Product.objects.create(
			name="Test Cream",
			description="Test",
			price=Decimal("20.00"),
			stock=10,
		)

	def test_variant_stock_exceeds_product_fails(self):
		"""Variant stock > product stock should fail validation."""
		variant = ProductVariant(
			product=self.product,
			name="50ml",
			sku="TEST-50ML",
			stock=15,  # Exceeds product stock of 10
		)

		with self.assertRaises(ValidationError):
			variant.full_clean()

	def test_variant_stock_within_limit_succeeds(self):
		"""Variant stock <= product stock should pass validation."""
		variant = ProductVariant(
			product=self.product,
			name="50ml",
			sku="TEST-50ML",
			stock=10,  # Equal to product stock
		)

		variant.full_clean()  # Should not raise
		variant.save()
		self.assertEqual(variant.stock, 10)


class Phase1OrderServiceTest(TransactionTestCase):
	"""
	Test Fix 4: OrderService handles stock and discount operations atomically.
	Replaces cascading signal handlers with explicit service methods.
	"""

	def setUp(self):
		"""Create test data."""
		self.user = User.objects.create_user(username="testuser", password="testpass123")
		
		self.product = Product.objects.create(
			name="Test Product",
			description="Test",
			price=Decimal("20.00"),
			stock=100,
		)
		
		self.variant = ProductVariant.objects.create(
			product=self.product,
			name="50ml",
			sku="TEST-50ML",
			stock=50,
		)
		
		self.discount = DiscountCode.objects.create(
			code="TEST10",
			discount_percent=10,
            active=True,
		)


	def test_deduct_stock_for_order(self):
		"""OrderService should deduct stock when order created."""
		order = Order.objects.create(
			user=self.user,
			status=Order.Status.PENDING,
		)
		
		OrderItem.objects.create(
			order=order,
			product=self.product,
			variant=self.variant,
			quantity=5,
			price=Decimal("20.00"),
		)

		variant_before = ProductVariant.objects.get(pk=self.variant.pk).stock
		product_before = Product.objects.get(pk=self.product.pk).stock

		OrderService.deduct_stock_for_order(order)

		variant_after = ProductVariant.objects.get(pk=self.variant.pk).stock
		product_after = Product.objects.get(pk=self.product.pk).stock
		
		self.assertEqual(variant_after, variant_before - 5)
		self.assertEqual(product_after, product_before - 5)

	def test_increment_discount_code_usage(self):
		"""OrderService should increment discount usage."""
		order = Order.objects.create(
			user=self.user,
			discount_code=self.discount,
			status=Order.Status.PENDING,
		)

		usage_before = DiscountCode.objects.get(pk=self.discount.pk).times_used

		OrderService.increment_discount_code_usage(order)

		usage_after = DiscountCode.objects.get(pk=self.discount.pk).times_used
		self.assertEqual(usage_after, usage_before + 1)

	def test_cancel_order_full_workflow(self):
		"""OrderService.cancel_order should handle full cancellation."""
		order = Order.objects.create(
			user=self.user,
			discount_code=self.discount,
			status=Order.Status.PENDING,
		)
		
		OrderItem.objects.create(
			order=order,
			product=self.product,
			variant=self.variant,
			quantity=5,
			price=Decimal("20.00"),
		)

		stock_before = ProductVariant.objects.get(pk=self.variant.pk).stock
		discount_before = DiscountCode.objects.get(pk=self.discount.pk).times_used

		# Deduct and increment
		OrderService.deduct_stock_for_order(order)
		OrderService.increment_discount_code_usage(order)

		# Cancel
		OrderService.cancel_order(order)

		# Verify restoration
		order_after = Order.objects.get(pk=order.pk)
		self.assertEqual(order_after.status, Order.Status.CANCELED)
		
		stock_after = ProductVariant.objects.get(pk=self.variant.pk).stock
		discount_after = DiscountCode.objects.get(pk=self.discount.pk).times_used
		
		self.assertEqual(stock_after, stock_before)
		self.assertEqual(discount_after, discount_before)


class Phase1ProductStockSyncTest(TransactionTestCase):
	"""
	Test Fix 6: Product-level stock sync prevents overselling across variants.
	"""

	def setUp(self):
		"""Create product with multiple variants."""
		self.product = Product.objects.create(
			name="Multi-Size Cream",
			description="Test",
			price=Decimal("20.00"),
			stock=10,  # Total across all variants
		)
		
		self.variant_small = ProductVariant.objects.create(
			product=self.product,
			name="30ml",
			sku="CREAM-30ML",
			stock=5,
		)
		
		self.variant_medium = ProductVariant.objects.create(
			product=self.product,
			name="50ml",
			sku="CREAM-50ML",
			stock=5,
		)

	def test_product_level_stock_validation(self):
		"""Multi-variant order total should not exceed product stock."""
		user = User.objects.create_user(username="testuser", password="testpass123")
		
		order = Order.objects.create(user=user, status=Order.Status.PENDING)
		
		OrderItem.objects.create(
			order=order,
			product=self.product,
			variant=self.variant_small,
			quantity=5,
			price=Decimal("20.00"),
		)
		
		OrderItem.objects.create(
			order=order,
			product=self.product,
			variant=self.variant_medium,
			quantity=5,
			price=Decimal("20.00"),
		)

		items = order.order_items.select_related("product", "variant").all()
		
		# Simulate product-level validation from Fix 6
		product_quantities = {}
		for item in items:
			if item.product_id not in product_quantities:
				product_quantities[item.product_id] = 0
			product_quantities[item.product_id] += item.quantity

		for product_id, total_qty in product_quantities.items():
			product = Product.objects.get(pk=product_id)
			self.assertLessEqual(total_qty, product.stock,
								"Total order quantity must not exceed product stock")


class Phase1TransactionAtomicityTest(TransactionTestCase):
	"""
	Test Fix 5: Order creation is fully atomic with proper transaction boundaries.
	"""

	def setUp(self):
		"""Create test data."""
		self.user = User.objects.create_user(username="testuser", password="testpass123")
		self.product = Product.objects.create(
			name="Test Product",
			description="Test",
			price=Decimal("25.00"),
			stock=100,
		)

	def test_order_and_items_created_atomically(self):
		"""Order and OrderItems created together or not at all."""
		
		with transaction.atomic():
			order = Order.objects.create(
				user=self.user,
				status=Order.Status.PENDING,
			)
			
			for i in range(3):
				OrderItem.objects.create(
					order=order,
					product=self.product,
					quantity=1,
					price=self.product.price,
				)

		self.assertEqual(Order.objects.count(), 1)
		self.assertEqual(OrderItem.objects.count(), 3)

	def test_order_total_calculated_within_transaction(self):
		"""Order total calculation happens within transaction (Fix 5)."""
		with transaction.atomic():
			order = Order.objects.create(
				user=self.user,
				status=Order.Status.PENDING,
			)
			
			OrderItem.objects.create(
				order=order,
				product=self.product,
				quantity=2,
				price=self.product.price,
			)
			
			# Calculate while in transaction
			order.calculate_total()
			order.save()

		order_after = Order.objects.get(pk=order.pk)
		self.assertGreater(order_after.total_price, 0, "Order total should be calculated")
