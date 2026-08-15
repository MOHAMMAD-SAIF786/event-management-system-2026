from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import AdminProfile


def cms_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        admin_user = getattr(request, "admin_user", None) or request.user
        if not admin_user or not admin_user.is_authenticated:
            return redirect("cms:admin_login")

        # Auto-provision superuser or staff as CMS Admin if profile missing
        if not hasattr(admin_user, "admin_profile"):
            if admin_user.is_superuser:
                AdminProfile.objects.create(user=admin_user, role="developer")
            elif admin_user.is_staff:
                AdminProfile.objects.create(user=admin_user, role="admin")
            else:
                messages.error(request, "Access denied. CMS Admin privileges required.")
                return redirect("cms:admin_login")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def superadmin_required(view_func):
    @wraps(view_func)
    @cms_login_required
    def _wrapped_view(request, *args, **kwargs):
        admin_user = getattr(request, "admin_user", None) or request.user
        if not hasattr(admin_user, "admin_profile") or not admin_user.admin_profile.is_superadmin():
            messages.error(request, "Access denied. Superadmin or Developer privileges required.")
            return redirect("cms:dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def developer_required(view_func):
    @wraps(view_func)
    @cms_login_required
    def _wrapped_view(request, *args, **kwargs):
        admin_user = getattr(request, "admin_user", None) or request.user
        if not hasattr(admin_user, "admin_profile") or not admin_user.admin_profile.is_developer():
            messages.error(request, "Access denied. Developer privileges required.")
            return redirect("cms:dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
