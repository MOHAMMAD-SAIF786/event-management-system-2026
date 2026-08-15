def customer_auth_context(request):
    """
    Exposes customer and admin authentication status to templates.
    """
    customer_user = getattr(request, "customer_user", None) or getattr(request, "user", None)
    admin_user = getattr(request, "admin_user", None)

    is_customer_authenticated = customer_user is not None and customer_user.is_authenticated
    is_admin_authenticated = admin_user is not None and admin_user.is_authenticated

    return {
        "customer_user": customer_user,
        "admin_user": admin_user,
        "is_customer_authenticated": is_customer_authenticated,
        "is_admin_authenticated": is_admin_authenticated,
    }
