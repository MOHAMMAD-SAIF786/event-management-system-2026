"""
Dual Session Authentication System
Provides dedicated session isolation between Public Customer accounts and CMS Admin accounts.
"""

from typing import Optional
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import load_backend
from django.utils.crypto import constant_time_compare

# Dedicated Session Keys
CUSTOMER_SESSION_KEY = "_customer_user_id"
CUSTOMER_BACKEND_KEY = "_customer_auth_backend"
CUSTOMER_HASH_KEY = "_customer_auth_hash"

CMS_ADMIN_SESSION_KEY = "_cms_admin_user_id"
CMS_ADMIN_BACKEND_KEY = "_cms_admin_backend"
CMS_ADMIN_HASH_KEY = "_cms_admin_hash"

DEFAULT_BACKEND = "django.contrib.auth.backends.ModelBackend"


# =========================================================================
# 1. CUSTOMER SESSION MANAGEMENT
# =========================================================================

def customer_login(request, user: User, backend: str = DEFAULT_BACKEND) -> None:
    """
    Log in a customer user into the customer session namespace.
    Preserves any active CMS admin session.
    """
    session_admin_id = request.session.get(CMS_ADMIN_SESSION_KEY)
    session_admin_backend = request.session.get(CMS_ADMIN_BACKEND_KEY)
    session_admin_hash = request.session.get(CMS_ADMIN_HASH_KEY)

    # Set customer keys
    request.session[CUSTOMER_SESSION_KEY] = str(user.pk)
    request.session[CUSTOMER_BACKEND_KEY] = getattr(user, "backend", backend)
    request.session[CUSTOMER_HASH_KEY] = user.get_session_auth_hash()

    # Clear standard Django fallback key if present
    request.session.pop("_auth_user_id", None)
    request.session.pop("_auth_user_backend", None)
    request.session.pop("_auth_user_hash", None)

    # Restore admin session if present
    if session_admin_id:
        request.session[CMS_ADMIN_SESSION_KEY] = session_admin_id
        request.session[CMS_ADMIN_BACKEND_KEY] = session_admin_backend
        request.session[CMS_ADMIN_HASH_KEY] = session_admin_hash

    # Attach to request
    request.customer_user = user
    request._cached_customer_user = user
    if not request.path.startswith("/cms/"):
        request.user = user
    request.session.modified = True


def customer_logout(request) -> None:
    """
    Log out customer user without logging out active CMS admin.
    """
    request.session.pop(CUSTOMER_SESSION_KEY, None)
    request.session.pop(CUSTOMER_BACKEND_KEY, None)
    request.session.pop(CUSTOMER_HASH_KEY, None)

    # If no separate admin session is active, also clear standard session keys
    if not request.session.get(CMS_ADMIN_SESSION_KEY):
        request.session.pop("_auth_user_id", None)
        request.session.pop("_auth_user_backend", None)
        request.session.pop("_auth_user_hash", None)

    if hasattr(request, "_cached_customer_user"):
        delattr(request, "_cached_customer_user")

    request.customer_user = AnonymousUser()
    if not request.path.startswith("/cms/"):
        request.user = AnonymousUser()
    request.session.modified = True


def get_customer_user(request) -> User | AnonymousUser:
    """
    Retrieve currently authenticated customer user from session.
    """
    if hasattr(request, "_cached_customer_user"):
        return request._cached_customer_user

    user_id = request.session.get(CUSTOMER_SESSION_KEY)
    session_hash = request.session.get(CUSTOMER_HASH_KEY)

    if not user_id:
        # Fallback to standard Django session if logged in via standard Django auth and not in CMS
        std_user_id = request.session.get("_auth_user_id")
        if std_user_id and not request.path.startswith("/cms/"):
            try:
                user = User.objects.get(pk=std_user_id, is_active=True)
                request._cached_customer_user = user
                return user
            except User.DoesNotExist:
                pass
        request._cached_customer_user = AnonymousUser()
        return request._cached_customer_user

    try:
        user = User.objects.get(pk=user_id, is_active=True)
        if session_hash:
            if not constant_time_compare(session_hash, user.get_session_auth_hash()):
                request.session.pop(CUSTOMER_SESSION_KEY, None)
                request.session.pop(CUSTOMER_HASH_KEY, None)
                request._cached_customer_user = AnonymousUser()
                return request._cached_customer_user
        request._cached_customer_user = user
        return user
    except User.DoesNotExist:
        request._cached_customer_user = AnonymousUser()
        return request._cached_customer_user


# =========================================================================
# 2. CMS ADMIN SESSION MANAGEMENT
# =========================================================================

def cms_admin_login(request, user: User, backend: str = DEFAULT_BACKEND) -> None:
    """
    Log in an admin into the CMS admin session namespace.
    Preserves any active Customer public session.
    """
    session_cust_id = request.session.get(CUSTOMER_SESSION_KEY)
    session_cust_backend = request.session.get(CUSTOMER_BACKEND_KEY)
    session_cust_hash = request.session.get(CUSTOMER_HASH_KEY)

    # Set admin keys
    request.session[CMS_ADMIN_SESSION_KEY] = str(user.pk)
    request.session[CMS_ADMIN_BACKEND_KEY] = getattr(user, "backend", backend)
    request.session[CMS_ADMIN_HASH_KEY] = user.get_session_auth_hash()

    # Restore customer session if present
    if session_cust_id:
        request.session[CUSTOMER_SESSION_KEY] = session_cust_id
        request.session[CUSTOMER_BACKEND_KEY] = session_cust_backend
        request.session[CUSTOMER_HASH_KEY] = session_cust_hash

    # Attach to request
    request.admin_user = user
    request._cached_admin_user = user
    if request.path.startswith("/cms/"):
        request.user = user
    request.session.modified = True


def cms_admin_logout(request) -> None:
    """
    Log out CMS admin without logging out active Customer user.
    """
    request.session.pop(CMS_ADMIN_SESSION_KEY, None)
    request.session.pop(CMS_ADMIN_BACKEND_KEY, None)
    request.session.pop(CMS_ADMIN_HASH_KEY, None)

    # If no separate customer session is active, also clear standard session keys
    if not request.session.get(CUSTOMER_SESSION_KEY):
        request.session.pop("_auth_user_id", None)
        request.session.pop("_auth_user_backend", None)
        request.session.pop("_auth_user_hash", None)

    if hasattr(request, "_cached_admin_user"):
        delattr(request, "_cached_admin_user")

    request.admin_user = AnonymousUser()
    if request.path.startswith("/cms/"):
        request.user = AnonymousUser()
    request.session.modified = True


def get_cms_admin_user(request) -> User | AnonymousUser:
    """
    Retrieve currently authenticated CMS admin user from session.
    """
    if hasattr(request, "_cached_admin_user"):
        return request._cached_admin_user

    user_id = request.session.get(CMS_ADMIN_SESSION_KEY)
    session_hash = request.session.get(CMS_ADMIN_HASH_KEY)

    if not user_id:
        # Fallback to standard session if superuser/staff logged in via standard admin
        std_user_id = request.session.get("_auth_user_id")
        if std_user_id and (request.path.startswith("/cms/") or request.path.startswith("/admin/")):
            try:
                user = User.objects.get(pk=std_user_id, is_active=True)
                if user.is_staff or user.is_superuser or hasattr(user, "admin_profile"):
                    request._cached_admin_user = user
                    return user
            except User.DoesNotExist:
                pass
        request._cached_admin_user = AnonymousUser()
        return request._cached_admin_user

    try:
        user = User.objects.get(pk=user_id, is_active=True)
        if session_hash:
            if not constant_time_compare(session_hash, user.get_session_auth_hash()):
                request.session.pop(CMS_ADMIN_SESSION_KEY, None)
                request.session.pop(CMS_ADMIN_HASH_KEY, None)
                request._cached_admin_user = AnonymousUser()
                return request._cached_admin_user
        request._cached_admin_user = user
        return user
    except User.DoesNotExist:
        request._cached_admin_user = AnonymousUser()
        return request._cached_admin_user


def update_customer_session_hash(request, user: User) -> None:
    """
    Update the customer session auth hash after password change.
    """
    request.session[CUSTOMER_HASH_KEY] = user.get_session_auth_hash()
    request.session.modified = True


def update_admin_session_hash(request, user: User) -> None:
    """
    Update the admin session auth hash after password change.
    """
    request.session[CMS_ADMIN_HASH_KEY] = user.get_session_auth_hash()
    request.session.modified = True
