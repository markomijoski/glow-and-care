"""
=============================================================================
  Glow & Care — Development Settings
  Use this locally. Never use in production.

  Activate:
      set DJANGO_SETTINGS_MODULE=CreamShop.settings.dev
  Or in manage.py / wsgi.py set it as the default.
=============================================================================
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]

# ---------------------------------------------------------------------------
# Database — local PostgreSQL
# (DATABASE_URL in .env e.g. postgres://user:pass@localhost:5432/creamshop_dev)
# ---------------------------------------------------------------------------
# Already configured in base.py via env.db("DATABASE_URL")

# ---------------------------------------------------------------------------
# Email — print to console instead of sending
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable mandatory email verification in dev so you can register freely
ACCOUNT_EMAIL_VERIFICATION = "none"

# ---------------------------------------------------------------------------
# Django Debug Toolbar (optional but highly recommended)
# pip install django-debug-toolbar
# ---------------------------------------------------------------------------
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ["debug_toolbar"]           # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
    DEBUG_TOOLBAR_CONFIG = {
        "IS_RUNNING_TESTS": True,
    }
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Media files served by Django in dev
# (In production this is handled by S3 or Nginx)
# ---------------------------------------------------------------------------
# No extra config needed — urls.py adds + static(MEDIA_URL, ...) in DEBUG mode

# ---------------------------------------------------------------------------
# Logging — show SQL queries and app logs in the console
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",   # change to DEBUG to print all SQL queries
            "propagate": False,
        },
        "creamapp": {             # app logger (used in signals.py)
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
