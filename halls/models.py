from django.db import models

# Create your models here.
class Hall(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    show_badge = models.BooleanField(
        default=False
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    capacity = models.IntegerField()
    image= models.ImageField(
        upload_to='hall/'
    )
    banner_image = models.ImageField(
        upload_to="hall/banner/",
        blank=True,
        null=True
    )
    location = models.CharField(
        max_length=200,
        blank=True
    )
    parking_capacity = models.IntegerField(
        default=0
    )
    is_ac = models.BooleanField(
    default=True
    )
    is_wifi = models.BooleanField(
    default=True
    )

    is_featured = models.BooleanField(
    default=False
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name 
    
class HallFeature(models.Model):

    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name="features"
    )

    icon = models.CharField(
        max_length=100
    )

    title = models.CharField(
        max_length=100
    )

    subtitle = models.CharField(
        max_length=100
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.hall.name} - {self.title}"

class HallGallery(models.Model):

    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name="gallery"
    )

    hall_image = models.ImageField(
        upload_to="hall/gallery/"
    )

    title = models.CharField(
        max_length=100,
        blank=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.hall.name} - Image {self.id}"
    
class FurnitureCategory(models.Model):

    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name="furniture_categories"
    )

    name = models.CharField(
        max_length=100
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.name
    
class FurnitureItem(models.Model):

    category = models.ForeignKey(
        FurnitureCategory,
        on_delete=models.CASCADE,
        related_name="items"
    )

    name = models.CharField(
        max_length=100
    )

    icon = models.CharField(
        max_length=50,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit = models.CharField(
        max_length=30
    )

    default_quantity = models.PositiveIntegerField(
        default=0
    )

    min_quantity = models.PositiveIntegerField(
        default=0
    )

    max_quantity = models.PositiveIntegerField(
        default=100
    )
    is_required = models.BooleanField(
    default=False
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.name
    
class StageCategory(models.Model):

    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name="stage_categories"
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class StageDesign(models.Model):

    category = models.ForeignKey(
        StageCategory,
        on_delete=models.CASCADE,
        related_name="designs"
    )

    name = models.CharField(max_length=100)

    badge = models.CharField(
        max_length=50,
        blank=True,
        default="New!",
        help_text="Badge text to display on stage card (e.g. New!, Popular, Trending)"
    )

    image = models.ImageField(
        upload_to="hall/stage/"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class ServiceCategory(models.Model):
    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name="service_categories"
    )

    name = models.CharField(max_length=100)
    subtitle = models.CharField(
    max_length=200,
    blank=True
    )
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.hall.name} - {self.name}"

class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name="services"
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class HallPage(models.Model):
    hero_title = models.CharField(
        max_length=200,
        default="Our Premium Banquet Halls"
    )
    hero_subtitle = models.TextField(
        default="Discover the perfect venue for your weddings, receptions, and corporate celebrations."
    )
    hero_badge = models.CharField(
        max_length=100,
        default="LUXURY VENUES"
    )
    hero_image = models.ImageField(
        upload_to="hall_page/",
        blank=True,
        null=True
    )

    def __str__(self):
        return "Hall Page Settings"