from django.db import models


class GalleryCategory(models.Model):
    name = models.CharField(
        max_length=100
    )  # e.g. Wedding, Corporate, Birthday
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Gallery Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class GalleryItem(models.Model):
    title = models.CharField(
        max_length=150, blank=True, help_text="Optional Title/Caption"
    )
    category = models.ForeignKey(
        GalleryCategory, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="gallery/")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title if self.title else f"Image {self.id}"


from django.contrib.auth.models import User


class AdminProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("superadmin", "Superadmin"),
        ("developer", "Developer"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="admin_profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="admin")
    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_cms_roles",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_developer(self):
        return self.role == "developer"

    def is_superadmin(self):
        return self.role in ("superadmin", "developer")

    def is_admin(self):
        return self.role in ("admin", "superadmin", "developer")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"