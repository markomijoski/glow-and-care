"""
URL configuration for CreamShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
=============================================================================
  Glow & Care — Root URL Configuration
=============================================================================
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Authentication (django-allauth handles login, register, password reset)
    path("accounts/", include("allauth.urls")),

    # App routes
    path("", include("creamapp.urls")),
]

# ---------------------------------------------------------------------------
# Serve media files in development
# In production, media is served by Nginx or S3 — NOT by Django.
# ---------------------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Django Debug Toolbar (only loaded if installed)
    try:
        import debug_toolbar
        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# ---------------------------------------------------------------------------
# Admin site branding
# ---------------------------------------------------------------------------
admin.site.site_header  = "Glow & Care Admin"
admin.site.site_title   = "Glow & Care"
admin.site.index_title  = "Store Management"
