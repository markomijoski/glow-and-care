"""
=============================================================================
  Glow & Care — Production Settings
  Only used on the live server.

  Activate:
      set DJANGO_SETTINGS_MODULE=CreamShop.settings.prod
=============================================================================
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405 set in .env.prod

# ---------------------------------------------------------------------------
# Security Headers
# ---------------------------------------------------------------------------
SECURE_HSTS_SECONDS            = 31536000   # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SECURE_SSL_REDIRECT            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = "DENY"

# ---------------------------------------------------------------------------
# Database — set DATABASE_URL in your production .env
# ---------------------------------------------------------------------------
# Already configured in base.py via env.db("DATABASE_URL")

# ---------------------------------------------------------------------------
# Email — production SMTP via Anymail + SendGrid (or Mailgun)
# pip install django-anymail[sendgrid]
# ---------------------------------------------------------------------------
# EMAIL_BACKEND    = "anymail.backends.sendgrid.EmailBackend"
# ANYMAIL = {
#     "SENDGRID_API_KEY": env("SENDGRID_API_KEY"),  # noqa: F405
# }

# ---------------------------------------------------------------------------
# Static & Media — WhiteNoise for static, AWS S3 for media uploads
# pip install django-storages boto3
# ---------------------------------------------------------------------------
# If using S3 for media, uncomment and configure:
#
# DEFAULT_FILE_STORAGE   = "storages.backends.s3boto3.S3Boto3Storage"
# AWS_ACCESS_KEY_ID      = env("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY  = env("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
# AWS_S3_REGION_NAME     = env("AWS_S3_REGION_NAME", default="eu-central-1")
# AWS_S3_CUSTOM_DOMAIN   = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
# MEDIA_URL              = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

# ---------------------------------------------------------------------------
# Caching — Redis (optional but recommended for sessions + template cache)
# pip install django-redis
# ---------------------------------------------------------------------------
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": env("REDIS_URL"),
#         "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
#     }
# }
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"

# ---------------------------------------------------------------------------
# Logging — write errors to file, send critical errors to admins via email
# ---------------------------------------------------------------------------
# ADMINS = [("Glow & Care Admin", env("ADMIN_EMAIL", default="admin@glowandcare.com"))]  # noqa: F405

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {  # Го сменивме 'file' во 'console'
            "level": "WARNING",
            "class": "logging.StreamHandler",  # Ова пишува во терминалот
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"], # Го користиме 'console'
            "level": "WARNING",
            "propagate": True,
        },
        "creamapp": {
            "handlers": ["console"], # Го користиме 'console'
            "level": "WARNING",
            "propagate": False,
        },
    },
}
