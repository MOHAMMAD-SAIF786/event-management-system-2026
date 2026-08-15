from django.shortcuts import render, get_object_or_404
from .models import Hall, HallPage
from booking.models import BookingHall

def halls_list(request):
    hall_page, _ = HallPage.objects.get_or_create(id=1)
    halls = Hall.objects.filter(is_active=True)
    for h in halls:
        dates = list(
            BookingHall.objects.filter(
                hall=h,
                booking__status__in=["confirmed", "pending"],
                booking__event_date__isnull=False
            ).values_list("booking__event_date", flat=True)
        )
        h.booked_dates_list = [d.strftime("%b %d, %Y") for d in dates if d]
        h.booked_dates_str = ", ".join(h.booked_dates_list)
    return render(request, "halls/halls.html", {"halls": halls, "hall_page": hall_page})

def hall_detail(request, slug):
    hall = get_object_or_404(
        Hall,
        slug=slug,
        is_active=True
    )
    halls = Hall.objects.filter(is_active=True)

    booked_bookings = BookingHall.objects.filter(
        hall=hall,
        booking__status__in=["confirmed", "pending"],
        booking__event_date__isnull=False
    ).select_related("booking")

    booked_dates = [b.booking.event_date.strftime("%b %d, %Y") for b in booked_bookings if b.booking.event_date]

    return render(
        request,
        "halls/hall_detail.html",
        {
            "hall": hall,
            "halls": halls,
            "booked_dates": booked_dates,
            "booked_dates_str": ", ".join(booked_dates),
            "has_booked_dates": len(booked_dates) > 0,
        }
    )
