"""Compatibility wrapper for Django settings.

Use environment-specific modules directly when possible:
- CreamShop.settings.dev
- CreamShop.settings.prod
"""

from .settings.dev import *  # noqa: F401,F403
