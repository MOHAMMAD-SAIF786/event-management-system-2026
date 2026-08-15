from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse


def customer_login_required(view_func):
    """
    Decorator for views that require customer authentication.
    Redirects to accounts:user_login with next parameter if not authenticated.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        customer = getattr(request, "customer_user", None) or request.user
        if not customer or not customer.is_authenticated:
            login_url = reverse("accounts:user_login")
            return redirect(f"{login_url}?next={request.get_full_path()}")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
