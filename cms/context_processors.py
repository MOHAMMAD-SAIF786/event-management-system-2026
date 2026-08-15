def cms_role_context(request):
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        if hasattr(user, "admin_profile"):
            profile = user.admin_profile
            return {
                "cms_admin_profile": profile,
                "cms_role": profile.role,
                "is_developer": profile.is_developer(),
                "is_superadmin": profile.is_superadmin(),
                "is_admin": profile.is_admin(),
                "is_cms_user": True,
            }
        elif user.is_superuser:
            return {
                "cms_admin_profile": None,
                "cms_role": "developer",
                "is_developer": True,
                "is_superadmin": True,
                "is_admin": True,
                "is_cms_user": True,
            }
        elif user.is_staff:
            return {
                "cms_admin_profile": None,
                "cms_role": "admin",
                "is_developer": False,
                "is_superadmin": False,
                "is_admin": True,
                "is_cms_user": True,
            }

    return {
        "cms_admin_profile": None,
        "cms_role": None,
        "is_developer": False,
        "is_superadmin": False,
        "is_admin": False,
        "is_cms_user": False,
    }
