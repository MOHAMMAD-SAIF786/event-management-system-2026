from django.db import models
from rooms.models import Room
from halls.models import (
    Hall,
    FurnitureItem,
    StageDesign,
    Service,
) 
from catering.models import CateringPackage
from accounts.models import Customer
# Create your models here.
class Booking(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="bookings"
)

    booking_date = models.DateTimeField(auto_now_add=True)

    event_date = models.DateField(
        null=True,
        blank=True
    )

    event_type = models.CharField(
        max_length=100,
        blank=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_guest = models.PositiveIntegerField(
        default=100
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )


    def __str__(self):
        return f"Booking #{self.id}"
    
class BookingHall(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="hall_booking"
    )

    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.hall.name
    
class BookingFurniture(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="furniture"
    )

    furniture = models.ForeignKey(
        FurnitureItem,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.furniture.name
    
class BookingStage(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="stage"
    )

    stage = models.ForeignKey(
        StageDesign,
        on_delete=models.CASCADE
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.stage.name
    
class BookingService(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="services"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.service.name
    

class BookingRoom(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="rooms"
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.booking.customer.name} - {self.room.name}"
    
class BookingCatering(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="catering"
    )

    package = models.ForeignKey(
        CateringPackage,
        on_delete=models.CASCADE
    )

    guest_count = models.PositiveIntegerField()

    price_per_plate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.booking.customer.name} - {self.package.name}"
    
class BookingMenuItem(models.Model):

    booking_catering = models.ForeignKey(
        BookingCatering,
        on_delete=models.CASCADE,
        related_name="menu_items"
    )

    section = models.CharField(
        max_length=100
    )

    item_name = models.CharField(
        max_length=200
    )

    def __str__(self):
        return f"{self.section} - {self.item_name}"
    

