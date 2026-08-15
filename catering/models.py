# Create your models here.
from django.db import models


class CateringPackage(models.Model):

    name = models.CharField(max_length=100)
    
    image = models.ImageField( upload_to="catering",
    blank=True,
    null=True) 

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField()
    
    css_class = models.CharField(
        max_length=50,
        blank=True
    )

    badge = models.CharField(
        max_length=100,
        blank=True
    )

    show_on_home = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


class CateringFeature(models.Model):

    package = models.ForeignKey(
        CateringPackage,
        on_delete=models.CASCADE,
        related_name='features'
    )

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name

class MenuSection(models.Model):

    package = models.ForeignKey(
        CateringPackage,
        on_delete=models.CASCADE,
        related_name='sections'
    )

    title = models.CharField(
        max_length=100
    )

    has_category = models.BooleanField(
        default=False
    )

    available_items = models.PositiveIntegerField(
        default=0
    )

    max_selection = models.PositiveIntegerField(
        default=0
    )

    order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.package.name} - {self.title}"
    
    
class MenuCategory(models.Model):

    section = models.ForeignKey(
        MenuSection,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    title = models.CharField(
        max_length=100
    )

    order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ['id']


    def __str__(self):
        return self.title
    
class MenuItem(models.Model):

    section = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name='items'
    )

    name = models.CharField(
        max_length=100
    )

    is_available = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    
class GuestPricing(models.Model):

    package = models.ForeignKey(
        CateringPackage,
        on_delete=models.CASCADE,
        related_name='guest_pricing'
    )

    guest_count = models.PositiveIntegerField()

    price_per_plate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.guest_count} Guests - ₹{self.price_per_plate}"

class BannarFeature(models.Model):

    package = models.ForeignKey(
        CateringPackage,
        on_delete=models.CASCADE,
        related_name='bannar_features'
    )

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


class CateringPage(models.Model):

    hero_title = models.CharField(
        max_length=200,
        default="Catering Packages"
    )

    hero_subtitle = models.TextField(
        default="Select the perfect menu for your event"
    )

    hero_image = models.ImageField(
        upload_to='catering_page/',
        blank=True,
        null=True
    )

    def __str__(self):
        return "Catering Page Settings"