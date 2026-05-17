/* =============================================================================
   Glow & Care — Main JavaScript
   Vanilla JS utilities. No build step required.
============================================================================= */

"use strict";

/* ---------------------------------------------------------------------------
   CSRF helper — reads the csrftoken cookie for AJAX POST requests
--------------------------------------------------------------------------- */
function getCsrfToken() {
  const name = "csrftoken";
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + "=")) {
      return decodeURIComponent(cookie.slice(name.length + 1));
    }
  }
  return null;
}

/* ---------------------------------------------------------------------------
   Generic AJAX POST helper
   Returns a Promise that resolves to parsed JSON.

   Usage:
     ajaxPost("/cart/add/", { product_id: 3, quantity: 1 })
       .then(data => console.log(data))
       .catch(err => console.error(err));
--------------------------------------------------------------------------- */
async function ajaxPost(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }
  return response.json();
}

/* ---------------------------------------------------------------------------
   Cart badge — update the navbar cart count without page reload
   Called after any add/update/remove cart AJAX response.
--------------------------------------------------------------------------- */
function updateCartBadge(count) {
  const badge = document.querySelector(".navbar .badge");
  if (count > 0) {
    if (badge) {
      // Update the nested span that contains the count (FIXED: was destroying nested structure)
      const countSpan = badge.querySelector(".small");
      if (countSpan) {
        countSpan.textContent = count;
      } else {
        badge.textContent = count;
      }
    } else {
      // Create badge if it didn't exist (cart was empty)
      const cartLink = document.querySelector(".gc-shell-icon-link[href*='cart']");
      if (cartLink) {
        const newBadge = document.createElement("span");
        newBadge.className =
          "position-absolute top-0 start-100 translate-middle badge rounded-circle bg-pink border border-white p-1";
        newBadge.innerHTML = '<span class="visually-hidden">items in cart</span><span class="small px-1">' + count + '</span>';
        cartLink.classList.add("position-relative");
        cartLink.appendChild(newBadge);
      }
    }
  } else if (badge) {
    badge.remove();
  }
}

/* ---------------------------------------------------------------------------
   Add to Cart — handles the "Add to Cart" button on product cards and
   product detail pages.

   Expects the button to have:
     data-product-id="<id>"
     data-variant-id="<id>"   (optional)
     data-url="/cart/add/"
--------------------------------------------------------------------------- */
document.addEventListener("click", async function (e) {
  const btn = e.target.closest("[data-add-to-cart]");
  if (!btn) return;

  e.preventDefault();

  const productId = btn.dataset.productId;
  const variantId = btn.dataset.variantId || null;
  const url = btn.dataset.url || "/cart/add/";
  const quantity = parseInt(btn.dataset.quantity || "1", 10);

  // Visual feedback
  const original = btn.innerHTML;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
  btn.disabled = true;

  try {
    const data = await ajaxPost(url, { product_id: productId, variant_id: variantId, quantity });
    updateCartBadge(data.cart_item_count);
    showToast("Added to cart!", "success");
  } catch (err) {
    showToast("Something went wrong. Please try again.", "danger");
    console.error(err);
  } finally {
    btn.innerHTML = original;
    btn.disabled = false;
  }
});

/* ---------------------------------------------------------------------------
   Quantity stepper — +/- buttons on cart page
   Expects:
     <button data-quantity-change="-1" data-item-id="<id>" data-url="/cart/update/">
     <input  data-quantity-input data-item-id="<id>" value="2">
     <button data-quantity-change="+1" data-item-id="<id>" data-url="/cart/update/">
--------------------------------------------------------------------------- */
document.addEventListener("click", async function (e) {
  const btn = e.target.closest("[data-quantity-change]");
  if (!btn) return;

  const delta = parseInt(btn.dataset.quantityChange, 10);
  const itemId = btn.dataset.itemId;
  const url = btn.dataset.url || "/cart/update/";
  const input = document.querySelector(`[data-quantity-input][data-item-id="${itemId}"]`);

  if (!input) return;

  const newQty = Math.max(1, parseInt(input.value, 10) + delta);
  input.value = newQty;

  try {
    const data = await ajaxPost(url, { item_id: itemId, quantity: newQty });
    updateCartBadge(data.cart_item_count);

    // Update subtotal display
    const subtotalEl = document.querySelector(`[data-item-subtotal="${itemId}"]`);
    if (subtotalEl && data.item_subtotal) {
      subtotalEl.textContent = data.item_subtotal;
    }
    // Update cart total
    const totalEl = document.querySelector("[data-cart-total]");
    if (totalEl && data.cart_total) {
      totalEl.textContent = data.cart_total;
    }
  } catch (err) {
    console.error(err);
  }
});

/* ---------------------------------------------------------------------------
   Toast notification helper
   Creates a Bootstrap 5 toast and appends it to a container.
--------------------------------------------------------------------------- */
function showToast(message, type = "info") {
  let container = document.querySelector(".gc-toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "gc-toast-container";
    document.body.appendChild(container);
  }

  const icons = {
    success: '<i class="bi bi-check2-circle fs-5"></i>',
    error: '<i class="bi bi-exclamation-triangle fs-5"></i>',
    danger: '<i class="bi bi-x-circle fs-5"></i>',
    info: '<i class="bi bi-info-circle fs-5"></i>',
  };

  const toast = document.createElement("div");
  const typeClass = type === "danger" ? "error" : type;
  toast.className = `gc-toast gc-toast-${typeClass}`;

  toast.innerHTML = `
    <div class="gc-toast-icon">
      ${icons[type] || icons.info}
    </div>
    <div class="gc-toast-content flex-grow-1">
      <div class="small fw-bold text-dark">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
      <div class="small text-muted">${message}</div>
    </div>
    <button type="button" class="btn-close small" style="font-size: 0.6rem;"></button>
  `;

  container.appendChild(toast);

  // Trigger entrance animation
  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  // Auto-remove
  const timer = setTimeout(() => {
    dismissToast(toast);
  }, 5000);

  toast.querySelector(".btn-close").addEventListener("click", () => {
    clearTimeout(timer);
    dismissToast(toast);
  });
}

function dismissToast(toast) {
  toast.classList.remove("show");
  toast.addEventListener("transitionend", () => {
    toast.remove();
  });
}

/* ---------------------------------------------------------------------------
   Discount code AJAX validation on checkout page
   Expects:
     <input id="discount-code-input" ...>
     <button id="apply-discount-btn" data-url="/checkout/apply-discount/">
     <div id="discount-feedback"></div>
--------------------------------------------------------------------------- */
const applyBtn = document.getElementById("apply-discount-btn");
if (applyBtn) {
  applyBtn.addEventListener("click", async function () {
    const code = document.getElementById("discount-code-input")?.value.trim();
    const feedback = document.getElementById("discount-feedback");
    if (!code) return;

    try {
      const data = await ajaxPost(applyBtn.dataset.url, { code });
      if (data.valid) {
        feedback.innerHTML = `<span class="text-success">✓ ${data.discount_percent}% discount applied!</span>`;
        // Update total display
        const totalEl = document.querySelector("[data-order-total]");
        if (totalEl && data.new_total) totalEl.textContent = data.new_total;
      } else {
        feedback.innerHTML = `<span class="text-danger">✗ ${data.error}</span>`;
      }
    } catch (err) {
      feedback.innerHTML = `<span class="text-danger">Something went wrong.</span>`;
    }
  });
}

/* ---------------------------------------------------------------------------
   Auto-dismiss Bootstrap alerts after 4 seconds
--------------------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".alert.alert-dismissible").forEach(function (el) {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert?.close();
    }, 4000);
  });

  const variantSelect = document.querySelector("[data-variant-select]");
  const priceEl = document.querySelector("[data-product-price]");
  const stockEl = document.getElementById("variant-stock");
  const addCartBtn = document.querySelector("[data-add-cart-detail]");
  const variantScript = document.getElementById("variant-data");

  if (variantSelect && priceEl && variantScript) {
    let variantMap = [];
    try {
      variantMap = JSON.parse(variantScript.textContent || "[]");
    } catch (err) {
      variantMap = [];
    }

    const updateVariantState = () => {
      const selectedId = parseInt(variantSelect.value || "0", 10);
      const selected = variantMap.find((v) => v.id === selectedId);
      if (!selected) return;

      priceEl.textContent = selected.price;

      if (stockEl) {
        stockEl.innerHTML = selected.in_stock
          ? '<span class="badge text-bg-success">In stock</span>'
          : '<span class="badge badge-out-of-stock">Out of stock</span>';
      }

      if (addCartBtn) {
        addCartBtn.dataset.variantId = String(selected.id);
        addCartBtn.disabled = !selected.in_stock;
      }
    };

    variantSelect.addEventListener("change", updateVariantState);
    updateVariantState();
  }

  const mainImage = document.getElementById("product-main-image");
  const thumbs = document.querySelectorAll("[data-gallery-thumb]");

  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      if (!mainImage) return;
      const newUrl = thumb.dataset.imageUrl;
      if (newUrl) {
        mainImage.src = newUrl;
      }
    });
  });

  if (mainImage) {
    const frame = mainImage.closest(".product-zoom-frame");
    if (frame && window.matchMedia("(hover: hover)").matches) {
      frame.addEventListener("mousemove", (event) => {
        const rect = frame.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        mainImage.style.transformOrigin = `${x}% ${y}%`;
      });
      frame.addEventListener("mouseleave", () => {
        mainImage.style.transformOrigin = "center center";
      });
    }
  }

  // Back to Top Logic
  const backToTop = document.getElementById("backToTop");
  if (backToTop) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 400) {
        backToTop.classList.add("show");
      } else {
        backToTop.classList.remove("show");
      }
    });
    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});
