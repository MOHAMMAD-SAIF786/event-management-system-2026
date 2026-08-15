"""
Dual Session Authentication Middleware
Attaches request.customer_user and request.admin_user, and scopes request.user depending on the URL path.
"""

from accounts.session_auth import get_customer_user, get_cms_admin_user


class DualSessionAuthMiddleware:
    """
    Middleware that establishes separate customer and CMS admin authentication contexts per request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Resolve both authentication contexts
        request.customer_user = get_customer_user(request)
        request.admin_user = get_cms_admin_user(request)

        # Route-scoped user assignment
        if request.path.startswith("/cms/"):
            request.user = request.admin_user
        else:
            request.user = request.customer_user

        response = self.get_response(request)
        return response
