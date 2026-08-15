from django.contrib import admin
from .models import CateringPackage, CateringFeature, MenuSection, MenuItem, MenuCategory, GuestPricing, BannarFeature, CateringPage


class CateringFeatureInline(admin.TabularInline):
    model = CateringFeature
    extra = 1

class BannarFeatureInline(admin.TabularInline):
    model = BannarFeature
    extra = 1

class GuestPricingInline(admin.TabularInline):
    model = GuestPricing
    extra = 1


@admin.register(CateringPackage)
class CateringPackageAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'price',
        'show_on_home',
        'is_active'
    )

    list_filter = (
        'show_on_home',
        'is_active'
    )

    search_fields = (
        'name',
    )

    inlines = [
        CateringFeatureInline,
        BannarFeatureInline,
        GuestPricingInline,
    ]

@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'package',
        'available_items',
        'max_selection',
        'order'
    )

    list_filter = (
        'package',
    )

admin.site.register(MenuCategory)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'section',
        'is_available'
    )

    list_filter = (
        'section',
        'is_available'
    )

    search_fields = (
        'name',
    )

from .models import GuestPricing

@admin.register(GuestPricing)
class GuestPricingAdmin(admin.ModelAdmin):

    list_display = (
        'package',
        'guest_count',
        'price_per_plate',
        'order'
    )

    list_filter = (
        'package',
    )

@admin.register(CateringPage)
class CateringPageAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'hero_subtitle')
