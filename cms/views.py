import os
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils.timezone import now
from booking.models import Booking, BookingHall, BookingStage, BookingCatering, BookingRoom, BookingMenuItem
from collections import defaultdict
from accounts.models import Customer
from halls.models import (
    Hall,
    HallFeature,
    HallGallery,
    FurnitureCategory,
    FurnitureItem,
    StageDesign,
    StageCategory,
    ServiceCategory,
    Service,
    HallPage
    )
from rooms.models import Room, RoomFeature, RoomPage
from home.models import HomePage
from catering.models import (
    BannarFeature,
    CateringPackage,
    CateringFeature,
    CateringPage,
    GuestPricing,
    MenuCategory,
    MenuItem,
    MenuSection,
)

from .models import GalleryCategory, GalleryItem, AdminProfile
from .decorators import cms_login_required, superadmin_required, developer_required
from accounts.session_auth import cms_admin_login, cms_admin_logout
from django.utils.text import slugify


# 1. ADMIN LOGIN VIEW
def admin_login(request):
    admin_user = getattr(request, "admin_user", None) or request.user
    if admin_user and admin_user.is_authenticated:
        if hasattr(admin_user, "admin_profile") or admin_user.is_superuser or admin_user.is_staff:
            if not hasattr(admin_user, "admin_profile"):
                role = "developer" if admin_user.is_superuser else "admin"
                AdminProfile.objects.create(user=admin_user, role=role)
            return redirect('cms:dashboard')

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            if user.is_superuser and not hasattr(user, "admin_profile"):
                AdminProfile.objects.create(user=user, role="developer")
            elif user.is_staff and not hasattr(user, "admin_profile"):
                AdminProfile.objects.create(user=user, role="admin")

            if hasattr(user, "admin_profile"):
                cms_admin_login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('cms:dashboard')
            else:
                messages.error(request, "Access denied. CMS Admin privileges required.")
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'cms/login.html')



@cms_login_required
def dashboard(request):
    homepage = HomePage.objects.first()
    if not homepage:
        homepage = HomePage.objects.create(hero_title="Royal Event Management", hero_description="Make Your Event Memorable")

    if request.method == "POST" and request.POST.get("action_type") == "update_home_hero":
        homepage.hero_title = request.POST.get("hero_title", homepage.hero_title)
        homepage.hero_description = request.POST.get("hero_description", homepage.hero_description)
        if request.FILES.get("hero_image"):
            homepage.hero_image = request.FILES.get("hero_image")
        homepage.save()
        messages.success(request, "Homepage Hero updated successfully!")
        return redirect("cms:dashboard")

    total_bookings = Booking.objects.count()

    pending_bookings = Booking.objects.filter(
        status="pending"
    ).count()

    confirmed_bookings = Booking.objects.filter(
        status="confirmed"
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status="cancelled"
    ).count()

    today_bookings = Booking.objects.filter(
        booking_date__date=now().date()
    ).count()

    revenue = Booking.objects.filter(
        status="confirmed"
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    pending_revenue = Booking.objects.filter(
        status="pending"
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    cancelled_revenue = Booking.objects.filter(
        status="cancelled"
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    projected_revenue = revenue + pending_revenue

    recent_bookings = Booking.objects.order_by(
        "-booking_date"
    )[:5]

    context = {

        "homepage": homepage,

        "total_bookings": total_bookings,

        "pending_bookings": pending_bookings,

        "confirmed_bookings": confirmed_bookings,

        "cancelled_bookings": cancelled_bookings,

        "today_bookings": today_bookings,

        "revenue": revenue,

        "pending_revenue": pending_revenue,

        "cancelled_revenue": cancelled_revenue,

        "projected_revenue": projected_revenue,

        "recent_bookings": recent_bookings,

    }

    return render(
        request,
        "cms/dashboard.html",
        context
    )


@cms_login_required
def admin_logout(request):
    cms_admin_logout(request)
    messages.info(request, "CMS Admin logged out successfully.")
    return redirect("cms:admin_login")

# ===========================
# BOOKINGS
# ===========================

def booking_list(request):

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    bookings = Booking.objects.select_related("customer").all().order_by("-id")

    if search:
        if search.isdigit():
            bookings = bookings.filter(
                Q(id=int(search)) |
                Q(customer__phone__icontains=search)
            )
        else:
            bookings = bookings.filter(
                Q(customer__name__icontains=search) |
                Q(event_type__icontains=search)
            )

    if status:
        bookings = bookings.filter(status=status)

    paginator = Paginator(bookings, 10)

    page = request.GET.get("page")

    bookings = paginator.get_page(page)

    return render(
        request,
        "cms/bookings/list.html",
        {
            "bookings": bookings,
            "search": search,
            "status": status,
        },
    )


def booking_detail(request, id):

    booking = get_object_or_404(
        Booking.objects.select_related(
            "customer",
            "hall_booking__hall",
            "stage__stage",
            "catering__package",
        ).prefetch_related(
            "rooms__room",
            "furniture__furniture",
            "services__service",
            "catering__menu_items",
        ),
        id=id
    )

    menu_sections = defaultdict(list)

    if hasattr(booking, "catering"):

        for item in booking.catering.menu_items.all():

            menu_sections[item.section].append(item)
            
    hall_total = booking.hall_booking.price if hasattr(booking, "hall_booking") else 0

    room_total = sum(room.subtotal for room in booking.rooms.all())

    furniture_total = sum(item.subtotal for item in booking.furniture.all())

    stage_total = booking.stage.price if hasattr(booking, "stage") else 0

    service_total = sum(service.price for service in booking.services.all())

    catering_total = booking.catering.total_price if hasattr(booking, "catering") else 0

    grand_total = (
       hall_total +
       room_total +
       furniture_total +
       stage_total +
       service_total +
       catering_total
    )

    if booking.status.lower() == 'confirmed':
        paid_amount = booking.total_amount
        remaining_amount = Decimal('0.00')
    elif booking.status.lower() == 'pending':
        paid_amount = Decimal('10000.00') if booking.total_amount > Decimal('10000.00') else Decimal('0.00')
        remaining_amount = booking.total_amount - paid_amount
    else:
        paid_amount = Decimal('0.00')
        remaining_amount = booking.total_amount

    return render(
        request,
        "cms/bookings/detail.html",
        {
            "booking": booking,
            "menu_sections": dict(menu_sections),
            "hall_total": hall_total,
            "room_total": room_total,
            "furniture_total": furniture_total,
            "stage_total": stage_total,
            "service_total": service_total,
            "catering_total": catering_total,
            "grand_total": grand_total,
            "paid_amount": paid_amount,
            "remaining_amount": remaining_amount,
        }
    )

@cms_login_required
def booking_add(request):
    halls = Hall.objects.all()
    stages = StageDesign.objects.all()
    caterings = CateringPackage.objects.prefetch_related('sections__categories__items').all()
    rooms = Room.objects.all()

    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "").strip()
        customer_phone = request.POST.get("customer_phone", "").strip()
        customer_email = request.POST.get("customer_email", "").strip()
        customer_address = request.POST.get("customer_address", "").strip()

        event_type = request.POST.get("event_type", "Wedding")
        event_date = request.POST.get("event_date")
        status = request.POST.get("status", "pending")
        total_amount = request.POST.get("total_amount", "0")
        total_guest_str = request.POST.get("total_guest", "100")
        hall_id = request.POST.get("hall_id")
        stage_id = request.POST.get("stage_id")
        catering_id = request.POST.get("catering_id")

        try:
            total_guest = int(total_guest_str)
        except (ValueError, TypeError):
            total_guest = 100

        if customer_phone:
            customer, _ = Customer.objects.get_or_create(
                phone=customer_phone,
                defaults={
                    "name": customer_name or "New Customer",
                    "email": customer_email,
                    "address": customer_address,
                }
            )
            if customer_name and customer.name != customer_name:
                customer.name = customer_name
                if customer_email:
                    customer.email = customer_email
                if customer_address:
                    customer.address = customer_address
                customer.save()
        else:
            customer = Customer.objects.create(
                name=customer_name or "Guest Customer",
                phone=customer_phone or "0000000000",
                email=customer_email,
                address=customer_address,
            )

        try:
            total_val = float(total_amount)
        except (ValueError, TypeError):
            total_val = 0.0

        booking = Booking.objects.create(
            customer=customer,
            event_type=event_type,
            event_date=event_date if event_date else None,
            status=status,
            total_amount=total_val,
            total_guest=total_guest,
        )

        # 1. Hall Selection
        if hall_id:
            try:
                hall = Hall.objects.get(id=hall_id)
                hall_price = getattr(hall, 'price', getattr(hall, 'price_per_day', 0))
                BookingHall.objects.create(
                    booking=booking,
                    hall=hall,
                    price=hall_price or 0
                )
            except Hall.DoesNotExist:
                pass

        # 2. Stage Selection
        if stage_id:
            try:
                stage = StageDesign.objects.get(id=stage_id)
                BookingStage.objects.create(
                    booking=booking,
                    stage=stage,
                    price=getattr(stage, 'price', 0) or 0
                )
            except StageDesign.DoesNotExist:
                pass

        # 3. Room Selection
        for room in rooms:
            qty_str = request.POST.get(f"room_qty_{room.id}", "0")
            try:
                qty = int(qty_str)
            except (ValueError, TypeError):
                qty = 0
            if qty > 0:
                subtotal = room.price * qty
                BookingRoom.objects.create(
                    booking=booking,
                    room=room,
                    quantity=qty,
                    price=room.price,
                    subtotal=subtotal
                )

        # 4. Catering Selection & Detailed Menu Items
        if catering_id:
            try:
                cat = CateringPackage.objects.get(id=catering_id)
                price_per_plate = getattr(cat, 'price', getattr(cat, 'price_per_plate', 0)) or 0
                catering_total = price_per_plate * total_guest
                booking_catering = BookingCatering.objects.create(
                    booking=booking,
                    package=cat,
                    guest_count=total_guest,
                    price_per_plate=price_per_plate,
                    total_price=catering_total
                )

                selected_menu_items = request.POST.getlist("selected_menu_items")
                if selected_menu_items:
                    items = MenuItem.objects.filter(id__in=selected_menu_items)
                    for mi in items:
                        sec_title = mi.section.section.title if hasattr(mi.section, 'section') else "Main Course"
                        BookingMenuItem.objects.create(
                            booking_catering=booking_catering,
                            section=sec_title,
                            item_name=mi.name
                        )
                else:
                    for sec in cat.sections.all():
                        for cat_group in sec.categories.all():
                            for mi in cat_group.items.filter(is_available=True):
                                BookingMenuItem.objects.create(
                                    booking_catering=booking_catering,
                                    section=sec.title,
                                    item_name=mi.name
                                )
            except CateringPackage.DoesNotExist:
                pass

        messages.success(request, f"Booking #BK-{booking.id} created successfully.")
        return redirect("cms:booking_detail", id=booking.id)

    return render(
        request,
        "cms/bookings/add.html",
        {
            "halls": halls,
            "stages": stages,
            "caterings": caterings,
            "rooms": rooms,
        }
    )

@cms_login_required
def booking_edit(request, id):

    booking = get_object_or_404(
        Booking,
        id=id
    )

    if request.method == "POST":

        booking.customer.name = request.POST.get("customer_name")
        booking.customer.phone = request.POST.get("customer_phone")
        booking.customer.email = request.POST.get("customer_email")

        booking.customer.save()

        booking.event_type = request.POST.get("event_type")
        booking.event_date = request.POST.get("event_date")
        booking.status = request.POST.get("status")

        booking.save()

        messages.success(
            request,
            "Booking Updated Successfully."
        )

        return redirect(
            "cms:booking_detail",
            id=booking.id
        )

    return render(
        request,
        "cms/bookings/edit.html",
        {
            "booking": booking
        }
    )
    
@cms_login_required
def booking_delete(request, id):

    booking = get_object_or_404(
        Booking,
        id=id
    )

    booking.status = "cancelled"

    booking.save()

    messages.success(
        request,
        "Booking Cancelled Successfully."
    )

    return redirect("cms:booking_list")
    
@cms_login_required
def customer_list(request):

    search = request.GET.get("search", "")

    customers = Customer.objects.annotate(

        total_bookings=Count("bookings"),

        total_spent=Sum("bookings__total_amount")

    ).order_by("-created_at")

    if search:

        customers = customers.filter(

            name__icontains=search

        ) | Customer.objects.filter(

            phone__icontains=search

        ) | Customer.objects.filter(

            email__icontains=search

        )

    paginator = Paginator(customers, 10)

    page = request.GET.get("page")

    customers = paginator.get_page(page)

    return render(

        request,

        "cms/customers/customer_list.html",

        {

            "customers": customers,

            "search": search,

        }

    )
    
from django.db.models import Sum

@cms_login_required
def customer_detail(request, id):

    customer = get_object_or_404(Customer, id=id)

    bookings = customer.bookings.all().order_by("-booking_date")

    total_spent = bookings.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    confirmed = bookings.filter(status="confirmed").count()

    pending = bookings.filter(status="pending").count()

    cancelled = bookings.filter(status="cancelled").count()

    return render(
        request,
        "cms/customers/customer_detail.html",
        {
            "customer": customer,
            "bookings": bookings,
            "total_spent": total_spent,
            "confirmed": confirmed,
            "pending": pending,
            "cancelled": cancelled,
        }
    )
    
@cms_login_required
def customer_edit(request, id):

    customer = get_object_or_404(
        Customer,
        id=id
    )

    if request.method == "POST":

        customer.name = request.POST.get("name")

        customer.phone = request.POST.get("phone")

        customer.email = request.POST.get("email")

        customer.address = request.POST.get("address")

        customer.save()

        messages.success(
            request,
            "Customer Updated Successfully."
        )

        return redirect(
            "cms:customer_detail",
            id=customer.id
        )

    return render(
        request,
        "cms/customers/customer_edit.html",
        {
            "customer": customer
        }
    )
    
@cms_login_required
def customer_delete(request, id):

    customer = get_object_or_404(
        Customer,
        id=id
    )

    if customer.bookings.exists():

        messages.error(
            request,
            "Customer cannot be deleted because booking records exist."
        )

        return redirect(
            "cms:customer_detail",
            id=customer.id
        )

    customer.delete()

    messages.success(
        request,
        "Customer deleted successfully."
    )

    return redirect("cms:customer_list")

@cms_login_required
def hall_list(request):
    hall_page, _ = HallPage.objects.get_or_create(id=1)

    if request.method == "POST":
        action = request.POST.get("action_type")
        if action == "update_hero":
            hall_page.hero_title = request.POST.get("hero_title", hall_page.hero_title)
            hall_page.hero_subtitle = request.POST.get("hero_subtitle", hall_page.hero_subtitle)
            hall_page.hero_badge = request.POST.get("hero_badge", hall_page.hero_badge)
            if "hero_image" in request.FILES:
                hall_page.hero_image = request.FILES["hero_image"]
            hall_page.save()
            messages.success(request, "Hall page hero settings updated successfully!")
            return redirect("cms:hall_list")

    halls = Hall.objects.all().order_by("-created_at")

    return render(
        request,
        "cms/halls/hall_list.html",
        {
            "halls": halls,
            "hall_page": hall_page,
        }
    )
    
@cms_login_required  
def hall_detail(request, id):

    hall = get_object_or_404(Hall, id=id)

    return render(
        request,
        "cms/halls/hall_detail.html",
        {
            "hall": hall
        }
    )
    
@cms_login_required
def hall_edit(request, id):

    hall = get_object_or_404(Hall, id=id)

    if request.method == "POST":

        hall.name = request.POST.get("name")
        hall.slug = slugify(request.POST.get("name"))
        hall.description = request.POST.get("description")
        hall.price = request.POST.get("price")
        hall.capacity = request.POST.get("capacity")
        hall.location = request.POST.get("location")
        hall.parking_capacity = request.POST.get("parking_capacity")

        hall.is_ac = "is_ac" in request.POST
        hall.is_wifi = "is_wifi" in request.POST
        hall.is_featured = "is_featured" in request.POST
        hall.is_active = "is_active" in request.POST
        hall.show_badge = "show_badge" in request.POST

        if request.FILES.get("image"):
            hall.image = request.FILES["image"]

        if request.FILES.get("banner_image"):
            hall.banner_image = request.FILES["banner_image"]

        hall.save()

        messages.success(request, "Hall updated successfully.")

        return redirect("cms:cms_hall_detail", id=hall.id)

    return render(
        request,
        "cms/halls/hall_edit.html",
        {
            "hall": hall,
        },
    )
    
@cms_login_required
def hall_add(request):

    if request.method == "POST":

        slug = slugify(request.POST.get("name"))
        hall = Hall.objects.create(

            name=request.POST.get("name"),
            slug=slug,
            description=request.POST.get("description"),
            price=request.POST.get("price"),
            capacity=request.POST.get("capacity"),
            location=request.POST.get("location"),
            parking_capacity=request.POST.get("parking_capacity"),

            is_ac="is_ac" in request.POST,
            is_wifi="is_wifi" in request.POST,
            is_featured="is_featured" in request.POST,
            is_active="is_active" in request.POST,
            show_badge="show_badge" in request.POST,

            image=request.FILES.get("image"),
            banner_image=request.FILES.get("banner_image"),
        )

        messages.success(request, "Hall created successfully.")

        return redirect("cms:cms_hall_detail", id=hall.id)

    return render(
        request,
        "cms/halls/hall_add.html"
    )

@cms_login_required
def hall_feature_add(request, hall_id):
    hall = get_object_or_404(Hall, id=hall_id)
    if request.method == "POST":
        title = request.POST.get("title")
        subtitle = request.POST.get("subtitle", "")
        icon = request.POST.get("icon") or "fa-solid fa-star"
        if title:
            HallFeature.objects.create(
                hall=hall,
                title=title,
                subtitle=subtitle,
                icon=icon,
                order=HallFeature.objects.filter(hall=hall).count() + 1,
            )
            messages.success(request, "Hall Feature Added Successfully")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else "cms:cms_hall_detail", id=hall.id)

@cms_login_required
def hall_feature_edit(request, id):
    feature = get_object_or_404(HallFeature, id=id)
    if request.method == "POST":
        feature.title = request.POST.get("title", feature.title)
        feature.subtitle = request.POST.get("subtitle", feature.subtitle)
        if request.POST.get("icon"):
            feature.icon = request.POST.get("icon")
        feature.save()
        messages.success(request, "Feature Updated Successfully")
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else "cms:cms_hall_detail", id=feature.hall.id)

    return render(
        request,
        "cms/halls/hall_feature_edit.html",
        {
            "feature": feature
        }
    )
    
@cms_login_required
def hall_feature_delete(request, id):
    feature = get_object_or_404(HallFeature, id=id)
    hall_id = feature.hall.id
    feature.delete()
    messages.success(request, "Feature Deleted")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else "cms:cms_hall_detail", id=hall_id)

@cms_login_required
def hall_toggle_status(request, id):
    hall = get_object_or_404(Hall, id=id)

    try:
        hall.is_active = not hall.is_active
        hall.save(update_fields=["is_active"])

        return JsonResponse({
            "status": "success",
            "is_active": hall.is_active,
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
        }, status=500)

@cms_login_required
def hall_delete(request, id):
    hall = get_object_or_404(Hall, id=id)
    hall.delete()
    messages.success(request, "Hall deleted successfully.")
    return redirect("cms:hall_list")

@cms_login_required
def hall_feature_save(request, hall_id):
    print("POST HIT")
    print(request.POST)
    hall = get_object_or_404(Hall, id=hall_id)

    if request.method == "POST":

        feature_id = request.POST.get("feature_id")

        if feature_id:

            feature = get_object_or_404(HallFeature, id=feature_id)

        else:

            feature = HallFeature(hall=hall)

            feature.icon = "fa-solid fa-check"

            feature.order = HallFeature.objects.filter(hall=hall).count() + 1

        feature.title = request.POST.get("title")

        feature.subtitle = request.POST.get("subtitle")

        feature.save()

        messages.success(request, "Feature Saved Successfully")

    return redirect("cms:hall_edit", id=hall.id)

@cms_login_required
def hall_gallery_save(request, hall_id):

    hall = get_object_or_404(Hall, id=hall_id)

    if request.method == "POST":

        if request.FILES.get("hall_image"):

            HallGallery.objects.create(

                hall=hall,

                hall_image=request.FILES["hall_image"],

                title=request.POST.get("title"),

                order=HallGallery.objects.filter(hall=hall).count()+1

            )

            messages.success(request, "Gallery Image Added Successfully")

    return redirect("cms:hall_edit", id=hall.id)


@cms_login_required
def hall_gallery_delete(request, id):

    gallery = get_object_or_404(HallGallery, id=id)

    hall_id = gallery.hall.id

    gallery.delete()

    messages.success(request, "Gallery Image Deleted")

    return redirect("cms:hall_edit", id=hall_id)


@cms_login_required
def furniture_add(request):

    hall_id = request.GET.get("hall")

    hall = None
    categories = None

    if hall_id:
        hall = get_object_or_404(Hall, id=hall_id)

        categories = FurnitureCategory.objects.filter(
            hall=hall
        ).order_by("order")

    halls = Hall.objects.all()

    return render(
        request,
        "cms/furnitures/furniture_add.html",
        {
            "hall": hall,
            "halls": halls,
            "categories": categories,
            "is_from_hall": bool(hall),
        }
    )
    
@cms_login_required
def furniture_save(request):
    if request.method == "POST":
        category_id = request.POST.get("category") or request.POST.get("category_id")
        if not category_id:
            messages.error(request, "Please select a furniture category.")
            return redirect("cms:furniture_add")

        category = get_object_or_404(FurnitureCategory, id=category_id)

        price = request.POST.get("price") or 0.00
        default_qty = request.POST.get("default_quantity") or 0
        min_qty = request.POST.get("min_quantity") or None
        max_qty = request.POST.get("max_quantity") or None

        FurnitureItem.objects.create(
            category=category,
            name=request.POST.get("name"),
            price=price,
            unit=request.POST.get("unit", ""),
            default_quantity=default_qty,
            min_quantity=min_qty,
            max_quantity=max_qty,
            is_required="is_required" in request.POST,
            order=FurnitureItem.objects.filter(category=category).count() + 1,
        )

        messages.success(request, "Furniture Added Successfully")
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else "cms:furniture_list")

    return redirect("cms:furniture_list")

@cms_login_required
def furniture_category_add(request):
    if request.method == "POST":
        hall_id = request.POST.get("hall")
        if not hall_id:
            messages.error(request, "Please select a hall first.")
            return redirect("cms:furniture_add")

        hall = get_object_or_404(Hall, id=hall_id)
        category_name = request.POST.get("category")

        if category_name:
            FurnitureCategory.objects.create(
                hall=hall,
                name=category_name,
                order=FurnitureCategory.objects.filter(hall=hall).count() + 1,
            )
            messages.success(request, "Category Created Successfully")

        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else "cms:furniture_list")

    return redirect("cms:furniture_list")

@cms_login_required
def furniture_category_delete(request, id):
    category = get_object_or_404(FurnitureCategory, id=id)
    category.delete()
    messages.success(request, "Furniture category deleted successfully.")

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else "cms:furniture_list")

@cms_login_required
def furniture_list(request):
    halls = Hall.objects.prefetch_related("furniture_categories__items").all()
    return render(
        request,
        "cms/furnitures/furniture_list.html",
        {
            "halls": halls,
        },
    )

@cms_login_required
def furniture_edit(request, id):
    item = get_object_or_404(FurnitureItem, id=id)

    if request.method == "POST":
        item.name = request.POST.get("name")
        item.price = request.POST.get("price") or 0.00
        item.unit = request.POST.get("unit", "")
        item.default_quantity = request.POST.get("default_quantity") or 0

        min_qty = request.POST.get("min_quantity")
        max_qty = request.POST.get("max_quantity")
        item.min_quantity = min_qty if min_qty else None
        item.max_quantity = max_qty if max_qty else None

        item.is_required = "is_required" in request.POST
        item.save()

        messages.success(request, "Furniture Updated Successfully.")

        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)

        return redirect("cms:furniture_list")

    halls = Hall.objects.all()
    categories = FurnitureCategory.objects.filter(hall=item.category.hall)
    return render(
        request,
        "cms/furnitures/furniture_edit.html",
        {
            "item": item,
            "halls": halls,
            "categories": categories,
        },
    )
@cms_login_required
def furniture_delete(request, id):

    furniture = get_object_or_404(
        FurnitureItem,
        id=id
    )

    hall = furniture.category.hall

    furniture.delete()

    messages.success(
        request,
        "Furniture Deleted Successfully."
    )

    return redirect("cms:furniture_list")
    
@cms_login_required
def load_furniture_categories(request, hall_id):

    categories = FurnitureCategory.objects.filter(
        hall_id=hall_id
    ).order_by("order")

    data = []

    for category in categories:

        data.append({
            "id": category.id,
            "name": category.name,
        })

    return JsonResponse(data, safe=False)

@cms_login_required
def stage_design_list(request):
    # Hall -> StageCategories -> Designs
    halls = Hall.objects.prefetch_related('stage_categories__designs').all()
    return render(request, 'cms/stages/stage_design_list.html', {'halls': halls})

@cms_login_required
def stage_design_add(request):
    if request.method == "POST":
        category_id = request.POST.get("category_id")
        name = request.POST.get("name")
        badge = request.POST.get("badge", "New!")
        price = request.POST.get("price") or 0.00
        image = request.FILES.get("image")

        category = get_object_or_404(StageCategory, id=category_id)

        StageDesign.objects.create(
            category=category,
            name=name,
            badge=badge,
            price=price,
            image=image
        )

        messages.success(request, "New Stage Design Added Successfully.")

        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect("cms:stage_design_list")

@cms_login_required
def stage_design_edit(request, id):
    design = get_object_or_404(StageDesign, id=id)

    if request.method == "POST":
        design.name = request.POST.get("name")
        design.badge = request.POST.get("badge", "")
        design.price = request.POST.get("price") or 0.00
        
        # Agar nayi image upload hui ho toh update karo
        if request.FILES.get("image"):
            design.image = request.FILES.get("image")

        design.save()
        messages.success(request, "Stage Design Updated Successfully.")

        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect("cms:stage_design_list")
    return redirect("cms:stage_design_list")


@cms_login_required
def stage_design_delete(request, id):
    design = get_object_or_404(StageDesign, id=id)
    design.delete()
    messages.success(request, "Stage Design Deleted Successfully.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect("cms:stage_design_list")

@cms_login_required
def stage_category_add(request):
    if request.method == "POST":
        hall_id = request.POST.get("hall_id")
        name = request.POST.get("name")
        description = request.POST.get("description", "")

        hall = get_object_or_404(Hall, id=hall_id)

        StageCategory.objects.create(
            hall=hall,
            name=name,
            description=description
        )

        messages.success(request, f"New Category '{name}' Added Successfully.")

        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect("cms:stage_design_list")
    return redirect("cms:stage_design_list")


@cms_login_required
def stage_category_delete(request, id):
    category = get_object_or_404(StageCategory, id=id)
    category.delete()
    messages.success(request, "Category Deleted Successfully.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect("cms:stage_design_list")

# 1. ADD SERVICE CATEGORY
@cms_login_required
def service_category_add(request):
    if request.method == "POST":
        hall_id = request.POST.get("hall_id")
        name = request.POST.get("name")
        subtitle = request.POST.get("subtitle", "")
        
        hall = get_object_or_404(Hall, id=hall_id)
        ServiceCategory.objects.create(
            hall=hall,
            name=name,
            subtitle=subtitle
        )
        messages.success(request, "New Service Category added successfully.")

        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else "cms:service_list")
    return redirect("cms:service_list")

# 2. DELETE SERVICE CATEGORY
@cms_login_required
def service_category_delete(request, id):
    category = get_object_or_404(ServiceCategory, id=id)
    category.delete()
    messages.success(request, "Service Category deleted successfully.")

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else "cms:service_list")

# 3. ADD SERVICE
@cms_login_required
def service_add(request):
    if request.method == "POST":
        category_id = request.POST.get("category_id")
        name = request.POST.get("name")
        raw_price = request.POST.get("price")
        try:
            price = min(Decimal(raw_price), Decimal('9999999999.99')) if raw_price else Decimal('0.00')
        except Exception:
            price = Decimal('0.00')

        category = get_object_or_404(ServiceCategory, id=category_id)
        Service.objects.create(
            category=category,
            name=name,
            price=price
        )
        messages.success(request, "New Service added successfully.")

        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else "cms:service_list")
    return redirect("cms:service_list")

# 4. EDIT SERVICE
@cms_login_required
def service_edit(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == "POST":
        service.name = request.POST.get("name")
        raw_price = request.POST.get("price")
        try:
            service.price = min(Decimal(raw_price), Decimal('9999999999.99')) if raw_price else Decimal('0.00')
        except Exception:
            service.price = Decimal('0.00')
        service.save()
        messages.success(request, "Service updated successfully.")

        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else "cms:service_list")
    return redirect("cms:service_list")

# 5. DELETE SERVICE
@cms_login_required
def service_delete(request, id):
    service = get_object_or_404(Service, id=id)
    service.delete()
    messages.success(request, "Service deleted successfully.")

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else "cms:service_list")

@cms_login_required
def service_list(request):
    halls = Hall.objects.prefetch_related('service_categories__services').all()
    
    return render(request, "cms/services/service_list.html", {"halls": halls})

@cms_login_required
def room_list(request):
    room_page, _ = RoomPage.objects.get_or_create(id=1)
    if request.method == 'POST' and request.POST.get('action_type') == 'update_hero':
        room_page.hero_title = request.POST.get('hero_title', room_page.hero_title)
        room_page.hero_subtitle = request.POST.get('hero_subtitle', room_page.hero_subtitle)
        if request.FILES.get('hero_image'):
            room_page.hero_image = request.FILES.get('hero_image')
        room_page.save()
        messages.success(request, 'Room page hero updated successfully!')
        return redirect('cms:room_list')

    rooms = Room.objects.prefetch_related('features').all()
    return render(request, 'cms/rooms/room_list.html', {'rooms': rooms, 'room_page': room_page})

# 2. Add Room
@cms_login_required
def room_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        capacity = request.POST.get('capacity')
        total_rooms = request.POST.get('total_rooms', 1)
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        features_str = request.POST.get('features', '')

        room = Room.objects.create(
            name=name,
            price=price,
            capacity=capacity,
            total_rooms=total_rooms,
            description=description,
            image=image
        )

        # Features add karne ke liye
        if features_str:
            feature_list = [f.strip() for f in features_str.split(',') if f.strip()]
            for feat in feature_list:
                RoomFeature.objects.create(room=room, name=feat)

        return redirect('cms:room_list')
    return redirect('cms:room_list')

# 3. Edit Room
@cms_login_required
def room_edit(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room.name = request.POST.get('name')
        room.price = request.POST.get('price') or 0.00
        room.capacity = request.POST.get('capacity') or 1
        room.total_rooms = request.POST.get('total_rooms') or 1
        room.description = request.POST.get('description', '')

        if request.FILES.get('image'):
            room.image = request.FILES.get('image')

        room.save()

        # Features Update
        features_str = request.POST.get('features', '')
        room.features.all().delete()
        if features_str:
            feature_list = [f.strip() for f in features_str.split(',') if f.strip()]
            for feat in feature_list:
                RoomFeature.objects.create(room=room, name=feat)

        messages.success(request, f"Room '{room.name}' updated successfully.")
        return redirect('cms:room_list')

    return redirect('cms:room_list')

# 4. Delete Room
def room_delete(request, room_id):
    try:
        # room_id se room fetch karein
        room = Room.objects.get(id=room_id)
        room.delete()
        messages.success(request, f'Room #{room_id} deleted successfully!')
    except Room.DoesNotExist:
        # Agar ID 7 database mein nahi hai, tab bhi crash hone se bachega
        messages.error(
            request,
            f'Room with ID #{room_id} does not exist or was already deleted!',
        )
    return redirect('cms:room_list')

@cms_login_required
def room_toggle_status(request, id):
    room = get_object_or_404(Room, id=id)
    room.is_active = not room.is_active
    room.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "is_active": room.is_active})
    messages.success(request, f"Room status updated to {'Active' if room.is_active else 'Inactive'}.")
    return redirect("cms:room_list")


def catering_dashboard(request):
    catering_page, _ = CateringPage.objects.get_or_create(id=1)
    if request.method == 'POST' and request.POST.get('action_type') == 'update_hero':
        catering_page.hero_title = request.POST.get('hero_title', catering_page.hero_title)
        catering_page.hero_subtitle = request.POST.get('hero_subtitle', catering_page.hero_subtitle)
        if request.FILES.get('hero_image'):
            catering_page.hero_image = request.FILES.get('hero_image')
        catering_page.save()
        messages.success(request, 'Catering page hero updated successfully!')
        return redirect('cms:catering_list')

    packages = CateringPackage.objects.prefetch_related(
        'features', 'bannar_features', 'guest_pricing', 'sections__categories__items'
    ).all()
    return render(request, 'cms/caterings/catering_list.html', {'packages': packages, 'catering_page': catering_page})


def catering_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description', '')
        badge = request.POST.get('badge', '')
        css_class = request.POST.get('css_class', '')
        show_on_home = request.POST.get('show_on_home') == 'on'
        image = request.FILES.get('image')

        slug = slugify(name)
        orig = slug
        c = 1
        while CateringPackage.objects.filter(slug=slug).exists():
            slug = f"{orig}-{c}"
            c += 1

        pkg = CateringPackage.objects.create(
            name=name, slug=slug, price=price, description=description,
            badge=badge, css_class=css_class, show_on_home=show_on_home, image=image
        )

        # 1. Package Features (Comma separated)
        features_str = request.POST.get('features', '')
        if features_str:
            for f in features_str.split(','):
                if f.strip():
                    CateringFeature.objects.create(package=pkg, name=f.strip())

        # 2. Banner Highlights (Comma separated)
        bannar_str = request.POST.get('bannar_features', '')
        if bannar_str:
            for b in bannar_str.split(','):
                if b.strip():
                    BannarFeature.objects.create(package=pkg, name=b.strip())

        return redirect('cms:catering_list')
    return redirect('cms:catering_list')

def catering_edit(request, package_id):
    pkg = get_object_or_404(CateringPackage, id=package_id)
    if request.method == 'POST':
        pkg.name = request.POST.get('name')
        pkg.price = request.POST.get('price')
        pkg.badge = request.POST.get('badge', '')
        pkg.css_class = request.POST.get('css_class', '')
        pkg.description = request.POST.get('description', '')
        pkg.show_on_home = request.POST.get('show_on_home') == 'on'

        if request.FILES.get('image'):
            pkg.image = request.FILES.get('image')

        pkg.save()

        # Update Features
        pkg.features.all().delete()
        features_str = request.POST.get('features', '')
        if features_str:
            for f in features_str.split(','):
                if f.strip():
                    CateringFeature.objects.create(package=pkg, name=f.strip())

        # Update Banner Features
        pkg.bannar_features.all().delete()
        bannar_str = request.POST.get('bannar_features', '')
        if bannar_str:
            for b in bannar_str.split(','):
                if b.strip():
                    BannarFeature.objects.create(package=pkg, name=b.strip())

        return redirect('cms:catering_list')
    
@cms_login_required
def catering_delete(request, package_id):
    pkg = get_object_or_404(CateringPackage, id=package_id)
    pkg.delete()
    messages.success(request, "Catering Package deleted successfully.")
    return redirect('cms:catering_list')

@cms_login_required
def catering_toggle_status(request, id):
    pkg = get_object_or_404(CateringPackage, id=id)
    pkg.is_active = not pkg.is_active
    pkg.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "is_active": pkg.is_active})
    messages.success(request, f"Catering package status updated to {'Active' if pkg.is_active else 'Inactive'}.")
    return redirect("cms:catering_list")

def catering_list(request):
    caterings = Room.objects.prefetch_related('features').all()
    return render(request, 'cms/rooms/catering_list.html', {'caterings': caterings})

@cms_login_required
def menu_section_add(request, package_id):
    pkg = get_object_or_404(CateringPackage, id=package_id)
    if request.method == "POST":
        title = request.POST.get("title")
        has_category = "has_category" in request.POST
        available_items = request.POST.get("available_items", 0)
        max_selection = request.POST.get("max_selection", 0)
        order = request.POST.get("order", 0)
        MenuSection.objects.create(
            package=pkg, title=title, has_category=has_category,
            available_items=available_items, max_selection=max_selection, order=order
        )
        messages.success(request, f"Menu Section '{title}' added successfully.")
    return redirect("cms:package_detail", pk=package_id)

@cms_login_required
def menu_section_edit(request, id):
    section = get_object_or_404(MenuSection, id=id)
    if request.method == "POST":
        section.title = request.POST.get("title", section.title)
        section.has_category = "has_category" in request.POST
        section.available_items = request.POST.get("available_items", section.available_items)
        section.max_selection = request.POST.get("max_selection", section.max_selection)
        section.order = request.POST.get("order", section.order)
        section.save()
        messages.success(request, "Menu Section updated successfully.")
    return redirect("cms:package_detail", pk=section.package.id)

@cms_login_required
def menu_section_delete(request, id):
    section = get_object_or_404(MenuSection, id=id)
    pkg_id = section.package.id
    section.delete()
    messages.success(request, "Menu Section deleted successfully.")
    return redirect("cms:package_detail", pk=pkg_id)

@cms_login_required
def menu_category_add(request, section_id):
    section = get_object_or_404(MenuSection, id=section_id)
    if request.method == "POST":
        title = request.POST.get("title")
        MenuCategory.objects.create(section=section, title=title)
        messages.success(request, f"Category '{title}' added successfully.")
    return redirect("cms:package_detail", pk=section.package.id)

@cms_login_required
def menu_category_delete(request, id):
    category = get_object_or_404(MenuCategory, id=id)
    pkg_id = category.section.package.id
    category.delete()
    messages.success(request, "Menu Category deleted successfully.")
    return redirect("cms:package_detail", pk=pkg_id)

@cms_login_required
def menu_item_add(request, category_id):
    category = get_object_or_404(MenuCategory, id=category_id)
    if request.method == "POST":
        item_names = request.POST.get("name", "")
        names = [n.strip() for n in item_names.replace('\n', ',').split(',') if n.strip()]
        for name in names:
            MenuItem.objects.create(section=category, name=name)
        messages.success(request, f"{len(names)} item(s) added successfully.")
    return redirect("cms:package_detail", pk=category.section.package.id)

@cms_login_required
def menu_item_delete(request, id):
    item = get_object_or_404(MenuItem, id=id)
    pkg_id = item.section.section.package.id
    item.delete()
    messages.success(request, "Menu Item deleted successfully.")
    return redirect("cms:package_detail", pk=pkg_id)

@cms_login_required
def menu_item_toggle(request, id):
    item = get_object_or_404(MenuItem, id=id)
    item.is_available = not item.is_available
    item.save()
    pkg_id = item.section.section.package.id
    messages.success(request, "Menu Item availability updated.")
    return redirect("cms:package_detail", pk=pkg_id)

@cms_login_required
def guest_pricing_add(request, package_id):
    pkg = get_object_or_404(CateringPackage, id=package_id)
    if request.method == "POST":
        guest_count = request.POST.get("guest_count")
        price_per_plate = request.POST.get("price_per_plate")
        GuestPricing.objects.create(package=pkg, guest_count=guest_count, price_per_plate=price_per_plate)
        messages.success(request, "Guest pricing tier added successfully.")
    return redirect("cms:package_detail", pk=package_id)

@cms_login_required
def guest_pricing_delete(request, id):
    pricing = get_object_or_404(GuestPricing, id=id)
    pkg_id = pricing.package.id
    pricing.delete()
    messages.success(request, "Guest pricing tier deleted successfully.")
    return redirect("cms:package_detail", pk=pkg_id)

@cms_login_required
def bannar_feature_add(request, package_id):
    pkg = get_object_or_404(CateringPackage, id=package_id)
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            BannarFeature.objects.create(package=pkg, name=name)
            messages.success(request, "Banner highlight added.")
    return redirect("cms:package_detail", pk=package_id)

@cms_login_required
def bannar_feature_delete(request, id):
    feature = get_object_or_404(BannarFeature, id=id)
    pkg_id = feature.package.id
    feature.delete()
    messages.success(request, "Banner highlight deleted.")
    return redirect("cms:package_detail", pk=pkg_id)

@cms_login_required
def catering_feature_add(request, package_id):
    pkg = get_object_or_404(CateringPackage, id=package_id)
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            CateringFeature.objects.create(package=pkg, name=name)
            messages.success(request, "Catering feature added.")
    return redirect("cms:package_detail", pk=package_id)

@cms_login_required
def catering_feature_delete(request, id):
    feature = get_object_or_404(CateringFeature, id=id)
    pkg_id = feature.package.id
    feature.delete()
    messages.success(request, "Catering feature deleted.")
    return redirect("cms:package_detail", pk=pkg_id)

def package_detail_view(request, pk):
    package = get_object_or_404(
        CateringPackage.objects.prefetch_related(
            "guest_pricing",
            "bannar_features",
            "sections__categories__items",
        ),
        pk=pk,
    )

    # --- DELETE REQUESTS (GET Query Parameters) ---
    if "delete_banner_tag" in request.GET:
        BannarFeature.objects.filter(
            id=request.GET.get("delete_banner_tag"), package=package
        ).delete()
        messages.success(request, "Banner tag deleted successfully.")
        return redirect("cms:package_detail", pk=package.pk)

    if "delete_pricing" in request.GET:
        GuestPricing.objects.filter(
            id=request.GET.get("delete_pricing"), package=package
        ).delete()
        messages.success(request, "Pricing slab deleted.")
        return redirect("cms:package_detail", pk=package.pk)

    if "delete_section" in request.GET:
        MenuSection.objects.filter(
            id=request.GET.get("delete_section"), package=package
        ).delete()
        messages.success(request, "Menu section deleted.")
        return redirect("cms:package_detail", pk=package.pk)

    if "delete_category" in request.GET:
        MenuCategory.objects.filter(
            id=request.GET.get("delete_category"), section__package=package
        ).delete()
        messages.success(request, "Category deleted.")
        return redirect("cms:package_detail", pk=package.pk)

    if "delete_item" in request.GET:
        MenuItem.objects.filter(
            id=request.GET.get("delete_item"), section__section__package=package
        ).delete()
        messages.success(request, "Menu item deleted.")
        return redirect("cms:package_detail", pk=package.pk)

    # --- ADD & EDIT REQUESTS (POST) ---
    if request.method == "POST":
        action = request.POST.get("action_type")

        # 1. Update Basic Package Info
        if action == "update_package_info":
            package.name = request.POST.get("name")
            package.price = request.POST.get("price")
            package.badge = request.POST.get("badge")
            package.description = request.POST.get("description")
            if "image" in request.FILES:
                package.image = request.FILES["image"]
            package.save()
            messages.success(request, "Package info updated.")

        # 2. Add / Edit Banner Tag
        elif action == "add_banner_tag":
            tag_name = request.POST.get("tag_name")
            if tag_name:
                BannarFeature.objects.create(package=package, name=tag_name)
                messages.success(request, "Banner tag added.")

        elif action == "edit_banner_tag":
            tag = get_object_or_404(
                BannarFeature, id=request.POST.get("tag_id"), package=package
            )
            tag.name = request.POST.get("tag_name")
            tag.save()
            messages.success(request, "Banner tag updated.")

        # 3. Add / Edit Guest Pricing
        elif action == "add_guest_pricing":
            GuestPricing.objects.create(
                package=package,
                guest_count=request.POST.get("guest_count"),
                price_per_plate=request.POST.get("price_per_plate"),
            )
            messages.success(request, "Guest pricing added.")

        elif action == "edit_guest_pricing":
            pricing = get_object_or_404(
                GuestPricing, id=request.POST.get("pricing_id"), package=package
            )
            pricing.guest_count = request.POST.get("guest_count")
            pricing.price_per_plate = request.POST.get("price_per_plate")
            pricing.save()
            messages.success(request, "Pricing updated.")

        # 4. Add / Edit Menu Section
        elif action == "add_section":
            MenuSection.objects.create(
                package=package,
                title=request.POST.get("section_title"),
                available_items=request.POST.get("available_items", 0),
                max_selection=request.POST.get("max_selection", 0),
            )
            messages.success(request, "Menu section created.")

        elif action == "edit_section":
            sec = get_object_or_404(
                MenuSection, id=request.POST.get("section_id"), package=package
            )
            sec.title = request.POST.get("section_title")
            sec.available_items = request.POST.get("available_items", 0)
            sec.max_selection = request.POST.get("max_selection", 0)
            sec.save()
            messages.success(request, "Section updated.")

        # 5. Add / Edit Category
        elif action == "add_category":
            sec = get_object_or_404(
                MenuSection, id=request.POST.get("section_id"), package=package
            )
            MenuCategory.objects.create(
                section=sec, title=request.POST.get("category_title")
            )
            messages.success(request, "Category added.")

        elif action == "edit_category":
            cat = get_object_or_404(
                MenuCategory,
                id=request.POST.get("category_id"),
                section__package=package,
            )
            cat.title = request.POST.get("category_title")
            cat.save()
            messages.success(request, "Category updated.")

        # 6. Add / Edit / Batch Add Items
        elif action == "add_item":
            cat = get_object_or_404(
                MenuCategory,
                id=request.POST.get("category_id"),
                section__package=package,
            )
            item_names = request.POST.get("item_name", "")
            # Support comma-separated or newline-separated items
            names = [n.strip() for n in item_names.replace('\n', ',').split(',') if n.strip()]
            for name in names:
                MenuItem.objects.create(section=cat, name=name)
            messages.success(request, f"{len(names)} item(s) added successfully.")

        elif action == "edit_item":
            item = get_object_or_404(
                MenuItem,
                id=request.POST.get("item_id"),
                section__section__package=package,
            )
            item.name = request.POST.get("item_name")
            item.save()
            messages.success(request, "Item updated.")


        return redirect("cms:package_detail", pk=package.pk)


    return render(
        request, "cms/caterings/package_detail.html", {"package": package}
    )
    
# 1. Main Website Frontend Gallery Page (Aam public ke liye)
def gallery_frontend_view(request):
    categories = GalleryCategory.objects.all()
    items = GalleryItem.objects.select_related("category").all()
    # Path ko 'cms/gallery.html' set karein
    return render(
        request, "gallery.html", {"categories": categories, "items": items}
    )


# 2. CMS Admin Dashboard Gallery Manager View
def cms_gallery_view(request):
    categories = GalleryCategory.objects.all()
    items = GalleryItem.objects.select_related("category").all()

    # 1. Delete Category Logic
    if "delete_category" in request.GET:
        GalleryCategory.objects.filter(
            id=request.GET.get("delete_category")
        ).delete()
        messages.success(request, "Category deleted successfully!")
        return redirect("cms:gallery_dashboard")

    # 2. Delete Image Logic
    if "delete_item" in request.GET:
        GalleryItem.objects.filter(id=request.GET.get("delete_item")).delete()
        messages.success(request, "Image deleted successfully!")
        cat_param = request.GET.get("category")
        if cat_param:
            return redirect(f"{reverse('cms:gallery_dashboard')}?category={cat_param}")
        return redirect("cms:gallery_dashboard")

    # 3. Category Filter Logic
    selected_category = request.GET.get("category")
    if selected_category:
        items = items.filter(category_id=selected_category)

    total_items_count = GalleryItem.objects.count()

    # 4. POST Requests (Add Category & Upload Images)
    if request.method == "POST":
        action = request.POST.get("action_type")

        # --- ADD CATEGORY ---
        if action == "add_category":
            cat_name = request.POST.get("name", "").strip()

            if cat_name:
                # Basic Slug Banayein
                base_slug = slugify(cat_name)
                slug = base_slug
                counter = 1

                # Unique Slug Auto-Generate Loop (IntegrityError Se Bachne Ke Liye)
                while GalleryCategory.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Check if category with exact name exists
                category, created = GalleryCategory.objects.get_or_create(
                    name=cat_name, defaults={"slug": slug}
                )

                if created:
                    messages.success(
                        request, f"Category '{cat_name}' added successfully!"
                    )
                else:
                    messages.warning(
                        request, f"Category '{cat_name}' already exists!"
                    )

        # --- UPLOAD IMAGES ---
        elif action == "upload_images":
            category_id = request.POST.get("category_id")
            images = request.FILES.getlist("images")
            title_input = request.POST.get("title", "").strip()

            if category_id and images:
                category = get_object_or_404(GalleryCategory, id=category_id)

                for index, img in enumerate(images, start=1):
                    if title_input:
                        img_title = f"{title_input} #{index}" if len(images) > 1 else title_input
                    else:
                        base_name = os.path.splitext(img.name)[0].replace("_", " ").replace("-", " ").title()
                        img_title = base_name if base_name else f"{category.name} Photo"

                    GalleryItem.objects.create(category=category, image=img, title=img_title)

                messages.success(
                    request,
                    f"{len(images)} Image(s) uploaded successfully to '{category.name}'!",
                )
            else:
                messages.error(
                    request, "Please select a category and at least one image."
                )

        return redirect("cms:gallery_dashboard")

    # Pagination for Gallery Items
    paginator = Paginator(items.order_by("-id"), 12)
    page = request.GET.get("page")
    items = paginator.get_page(page)

    # Render Template
    return render(
        request,
        "cms/gallery.html",
        {
            "categories": categories,
            "items": items,
            "selected_category": selected_category,
            "total_items_count": total_items_count,
        },
    )
    
def cms_login_view(request):
    # Agar user pehle se logged in hai toh direct dashboard bhej do
    if request.user.is_authenticated:
        return redirect("cms:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_staff or user.is_superuser:
                    auth_login(request, user)
                    messages.success(
                        request, f"Welcome back, {user.username}!"
                    )
                    return redirect("cms:dashboard")
                else:
                    messages.error(
                        request,
                        "Access Denied: You do not have CMS Admin privileges.",
                    )
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "cms/login.html", {"form": form})


def cms_logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('cms:login')


@cms_login_required
def cms_dashboard(request):
    return dashboard(request)



def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation Checks
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'cms/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'cms/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered!')
            return render(request, 'cms/register.html')

        # Create user and hash password securely
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, 'Account created successfully! Please login.')
        return redirect('cms:login')

    return render(request, 'cms/register.html')


@superadmin_required
def admin_management(request):
    if request.method == "POST":
        action = request.POST.get("action")
        target_user_id = request.POST.get("user_id")
        target_user = get_object_or_404(User, id=target_user_id)

        if action == "assign_admin":
            profile, created = AdminProfile.objects.get_or_create(user=target_user)
            if profile.role not in ("developer", "superadmin"):
                profile.role = "admin"
                profile.assigned_by = request.user
                profile.save()
                messages.success(request, f"Assigned Admin role to '{target_user.username}'.")
            else:
                messages.warning(request, f"User '{target_user.username}' already has higher role ({profile.get_role_display()}).")

        elif action == "revoke_admin":
            if hasattr(target_user, "admin_profile"):
                if target_user.admin_profile.role == "admin":
                    target_user.admin_profile.delete()
                    messages.success(request, f"Revoked Admin role from '{target_user.username}'.")
                else:
                    messages.error(request, "Superadmins cannot revoke Superadmin or Developer roles.")

        return redirect("cms:admin_management")

    admin_profiles_qs = AdminProfile.objects.select_related("user", "assigned_by").order_by("role", "-id")
    paginator = Paginator(admin_profiles_qs, 10)
    page = request.GET.get("page")
    admin_profiles = paginator.get_page(page)

    non_admin_users = User.objects.filter(admin_profile__isnull=True).order_by("username")

    return render(request, "cms/admin_management.html", {
        "admin_profiles": admin_profiles,
        "non_admin_users": non_admin_users,
    })


@developer_required
def developer_panel(request):
    if request.method == "POST":
        action = request.POST.get("action")
        target_user_id = request.POST.get("user_id")
        new_role = request.POST.get("role", "admin")
        target_user = get_object_or_404(User, id=target_user_id)

        if action == "update_role":
            profile, created = AdminProfile.objects.get_or_create(user=target_user)
            profile.role = new_role
            profile.assigned_by = request.user
            profile.save()
            messages.success(request, f"Updated role for '{target_user.username}' to {profile.get_role_display()}.")

        elif action == "revoke_role":
            if hasattr(target_user, "admin_profile"):
                target_user.admin_profile.delete()
                messages.success(request, f"Removed all CMS privileges from '{target_user.username}'.")

        return redirect("cms:developer_panel")

    all_users_qs = User.objects.select_related("admin_profile").order_by("-id")
    paginator = Paginator(all_users_qs, 12)
    page = request.GET.get("page")
    all_users = paginator.get_page(page)

    return render(request, "cms/developer_panel.html", {
        "all_users": all_users,
    })
