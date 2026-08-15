from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
import json
from decimal import Decimal
from .models import (
    Booking,
    BookingHall,
    BookingRoom,
    BookingFurniture,
    BookingStage,
    BookingService,
    BookingCatering,
    BookingMenuItem,
)
from accounts.models import Customer
from halls.models import (
    Hall,
    FurnitureItem,
    StageDesign,
    Service,
)
from rooms.models import Room
from catering.models import CateringPackage

# Create your views here.
def create_booking(request):

    try:
        data = json.loads(request.body)
        customer_data = data.get("customer", {})

        with transaction.atomic():
            # ---------------- CUSTOMER ----------------
            if request.user.is_authenticated:
                customer, created = Customer.objects.get_or_create(
                    user=request.user,
                    defaults={
                        "phone": customer_data.get("phone", ""),
                        "name": customer_data.get("name", ""),
                        "email": customer_data.get("email", ""),
                        "address": customer_data.get("address", ""),
                    },
                )
                if not created:
                    if customer_data.get("name"):
                        customer.name = customer_data["name"]
                    if customer_data.get("email"):
                        customer.email = customer_data["email"]
                    if customer_data.get("phone"):
                        customer.phone = customer_data["phone"]
                    customer.save()
            else:
                customer, created = Customer.objects.get_or_create(
                    phone=customer_data.get("phone", ""),
                    defaults={
                        "name": customer_data.get("name", "Guest Customer"),
                        "email": customer_data.get("email", ""),
                        "address": customer_data.get("address", ""),
                    },
                )

            # ---------------- BOOKING ----------------
            booking = Booking.objects.create(
                customer=customer,
                event_date=customer_data.get("event_date") or None,
                event_type=customer_data.get("event_type", "Wedding"),
                total_guest=int(customer_data.get("guests", 100)) if customer_data.get("guests") else 100,
            )

            total_amount = Decimal("0.00")

            # =================================================
            # HALL (Authoritative DB Price)
            # =================================================
            hall_data = data.get("hall")
            if hall_data and hall_data.get("id"):
                hall = Hall.objects.get(id=hall_data["id"])
                hall_price = hall.price
                BookingHall.objects.create(
                    booking=booking,
                    hall=hall,
                    price=hall_price
                )
                total_amount += hall_price

            # =================================================
            # ROOMS (Authoritative DB Price & Server Subtotal)
            # =================================================
            for item in data.get("rooms", []):
                if not item.get("id"):
                    continue
                room = Room.objects.get(id=item["id"])
                quantity = max(0, int(item.get("quantity", 0)))
                if quantity > 0:
                    price = room.price
                    subtotal = price * quantity
                    BookingRoom.objects.create(
                        booking=booking,
                        room=room,
                        quantity=quantity,
                        price=price,
                        subtotal=subtotal
                    )
                    total_amount += subtotal

            # =================================================
            # FURNITURE (Authoritative DB Price & Server Subtotal)
            # =================================================
            for item in data.get("furniture", []):
                if not item.get("id"):
                    continue
                furniture = FurnitureItem.objects.get(id=item["id"])
                quantity = max(0, int(item.get("quantity", 0)))
                if quantity > 0:
                    price = furniture.price
                    subtotal = price * quantity
                    BookingFurniture.objects.create(
                        booking=booking,
                        furniture=furniture,
                        quantity=quantity,
                        price=price,
                        subtotal=subtotal
                    )
                    total_amount += subtotal

            # =================================================
            # STAGE (Authoritative DB Price)
            # =================================================
            stage_data = data.get("stage")
            if stage_data and stage_data.get("id"):
                stage = StageDesign.objects.get(id=stage_data["id"])
                stage_price = stage.price
                BookingStage.objects.create(
                    booking=booking,
                    stage=stage,
                    price=stage_price
                )
                total_amount += stage_price

            # =================================================
            # ADDITIONAL SERVICES (Authoritative DB Price)
            # =================================================
            services = data.get("services", [])
            if not services:
                services = (
                    data.get("entertainment", [])
                    + data.get("photography", [])
                    + data.get("guestServices", [])
                )

            for item in services:
                if not item.get("id"):
                    continue
                service = Service.objects.get(id=item["id"])
                service_price = service.price
                BookingService.objects.create(
                    booking=booking,
                    service=service,
                    price=service_price
                )
                total_amount += service_price

            # =================================================
            # CATERING (Authoritative DB Price & Server Total)
            # =================================================
            catering_data = data.get("catering")
            if catering_data and catering_data.get("id"):
                package = CateringPackage.objects.get(id=catering_data["id"])
                guest_count = max(1, int(catering_data.get("guestCount", booking.total_guest or 100)))
                price_per_plate = package.price
                catering_total = price_per_plate * guest_count

                booking_catering = BookingCatering.objects.create(
                    booking=booking,
                    package=package,
                    guest_count=guest_count,
                    price_per_plate=price_per_plate,
                    total_price=catering_total
                )
                total_amount += catering_total

                # MENU ITEMS
                for menu in catering_data.get("selectedItems", []):
                    BookingMenuItem.objects.create(
                        booking_catering=booking_catering,
                        section=menu.get("section", ""),
                        item_name=menu.get("item", "")
                    )

            # =================================================
            # AUTHORITATIVE SERVER-SIDE TOTAL AMOUNT
            # =================================================
            booking.total_amount = total_amount
            booking.save(update_fields=["total_amount"])

            return JsonResponse({
                "status": "success",
                "booking_id": booking.id
            })


    except Exception as e:

        return JsonResponse(
            {
                "status": "error",
                "message": str(e)
            },
            status=400
        )
            
        
def quotation(request, booking_id):

    booking = get_object_or_404(

        Booking.objects.prefetch_related(

            "rooms",

            "furniture",

            "services",

            "catering__menu_items"

        ).select_related(
            "customer",
            "hall_booking__hall",
            "stage__stage",
            "catering__package"
        ),

        id=booking_id

    )

    return render(

        request,

        "quotation.html",

        {

            "booking": booking

        }

    )
    
def booking_overview(request):
    return render(request, "booking_overview.html")
    
