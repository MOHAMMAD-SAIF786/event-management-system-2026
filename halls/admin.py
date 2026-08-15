from django.contrib import admin
from .models import Hall,HallFeature,HallGallery,FurnitureCategory,FurnitureItem,StageCategory,StageDesign,ServiceCategory,Service,HallPage

@admin.register(HallPage)
class HallPageAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'hero_badge')
# Register your models here.

# ---------------- Hall ----------------

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'capacity',
        'is_active'
    )

    prepopulated_fields= {
        'slug': ('name',)
    }

# ---------------- Hall Feature ----------------

@admin.register(HallFeature)
class HallFeatureAdmin(admin.ModelAdmin):

    list_display = (
        "hall",
        "title",
        "order"
    )

    list_filter = (
        "hall",
    )

    ordering = (
        "hall",
        "order"
    )

# ---------------- Gallery ----------------

@admin.register(HallGallery)
class HallGalleryAdmin(admin.ModelAdmin):

    list_display = (
        "hall",
        "title",
        "order"
    )

    list_filter = (
        "hall",
    )

    ordering = (
        "hall",
        "order"
    )

# ---------------- Furniture ----------------

@admin.register(FurnitureCategory)
class FurnitureCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "hall",
        "name",
        "order",
    )

    ordering = (
        "hall",
        "order",
    )


@admin.register(FurnitureItem)
class FurnitureItemAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "name",
        "price",
        "unit",
        "order",
    )

    ordering = (
        "category",
        "order",
    )

# ---------------- Stage ----------------

@admin.register(StageCategory)
class StageCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "hall",
        "name",
        "order",
    )

    ordering = (
        "hall",
        "order",
    )


@admin.register(StageDesign)
class StageDesignAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "name",
        "price",
        "order",
    )

    ordering = (
        "category",
        "order",
    )

# ---------------- Services ----------------

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "hall",
        "name",
        "order",
    )

    ordering = (
        "hall",
        "order",
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "name",
        "price",
        "order",
    )

    ordering = (
        "category",
        "order",
    )