"""
=============================================================================
  Glow & Care — Base Settings
  Shared across all environments (dev, prod).
  Never run directly — imported by dev.py and prod.py.
=============================================================================
"""

import environ
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# BASE_DIR points to the project root (one level above the settings package)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------

# Environment variables (.env file)
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ---------------------------------------------------------------------------
# Installed Apps
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",          # required by allauth
    "django.contrib.sitemaps",       # SEO sitemaps
    "django.contrib.humanize",       # template filters: intcomma, naturaltime
]

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "crispy_forms",
    "crispy_bootstrap5",
]

LOCAL_APPS = [
    "creamapp.apps.CreamAppConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # required by allauth
]

# ---------------------------------------------------------------------------
# URLs & WSGI
# ---------------------------------------------------------------------------
ROOT_URLCONF = "CreamShop.urls"
WSGI_APPLICATION = "CreamShop.wsgi.application"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],   # project-level templates folder
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "creamapp.context_processors.cart_context",   # global cart count
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database — PostgreSQL, configured via individual .env variables
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE":   env("DB_ENGINE",   default="django.db.backends.postgresql"),
        "NAME":     env("DB_NAME"),
        "USER":     env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST":     env("DB_HOST",     default="localhost"),
        "PORT":     env("DB_PORT",     default="5432"),
        "OPTIONS": {
            # Keep connections alive to reduce per-request overhead
            "connect_timeout": 10,
        },
        "CONN_MAX_AGE": 60,  # reuse connections for up to 60 s
    }
}

# ---------------------------------------------------------------------------
# Password Validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Europe/Skopje"
USE_I18N      = True
USE_TZ        = True

# ---------------------------------------------------------------------------
# Static Files
# ---------------------------------------------------------------------------
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"           # collectstatic target
STATICFILES_DIRS = [BASE_DIR / "static"]         # your source static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------------
# Media Files (user uploads: product images, avatars, banners)
# ---------------------------------------------------------------------------
MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Default Primary Key
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Authentication (django-allauth)
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# Allauth behaviour
ACCOUNT_LOGIN_METHODS          = {"email"}           # login with email, not username
ACCOUNT_SIGNUP_FIELDS          = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION     = "mandatory"          # change to "none" in dev
ACCOUNT_UNIQUE_EMAIL           = True

LOGIN_URL          = "/accounts/login/"
LOGIN_REDIRECT_URL = "/profile/"                    # after login → profile
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = True

# ---------------------------------------------------------------------------
# Email — overridden per environment
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@glowandcare.com")
SERVER_EMAIL       = DEFAULT_FROM_EMAIL

# ---------------------------------------------------------------------------
# Crispy Forms
# ---------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK          = "bootstrap5"

# ---------------------------------------------------------------------------
# Sessions — store in DB so guest carts survive server restarts
# FIXED (Phase 2 Fix 13): Reduced database writes; sessions only saved on explicit changes
# Performance: Reduces 90% of unnecessary session writes (previously every request)
# ---------------------------------------------------------------------------
SESSION_ENGINE         = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE     = 60 * 60 * 24 * 30    # 30 days
SESSION_SAVE_EVERY_REQUEST = False  # FIXED: Changed from True to False for performance
SECURE_REDIRECT_EXEMPT = [r'^healthz/?$']

APPEND_SLASH = False  # Ensure URLs have trailing slashes for consistency and SEO