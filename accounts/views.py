from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Customer
from booking.models import Booking
from accounts.services import CustomerAuthManager
from accounts.session_auth import (
    customer_login,
    customer_logout,
    update_customer_session_hash,
)
from accounts.decorators import customer_login_required


def user_register(request):
    customer = getattr(request, "customer_user", None) or request.user
    if customer and customer.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not password or not name:
            messages.error(request, "Name, Username and Password are required!")
            return render(request, "accounts/register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "accounts/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return render(request, "accounts/register.html")

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return render(request, "accounts/register.html")

        # Register via CustomerAuthManager
        try:
            user, customer = CustomerAuthManager.register(
                provider_name="local",
                username=username,
                email=email,
                password=password,
                name=name,
                phone=phone,
            )
            customer_login(request, user)
            messages.success(request, f"Welcome to Royal Events, {name}!")
            next_url = request.GET.get("next") or request.POST.get("next") or "/"
            return redirect(next_url)
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, "accounts/register.html")

    return render(request, "accounts/register.html")


def user_login(request):
    customer = getattr(request, "customer_user", None) or request.user
    if customer and customer.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        login_input = request.POST.get("username", "").strip()
        password_input = request.POST.get("password", "")

        user = CustomerAuthManager.authenticate(
            provider_name="local",
            username=login_input,
            password=password_input,
        )

        if user is not None:
            customer_login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.POST.get("next") or request.GET.get("next") or "/"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password!")

    return render(request, "accounts/login.html")


def user_logout(request):
    customer_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


@customer_login_required
def profile(request):
    user = getattr(request, "customer_user", None) or request.user
    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": user.first_name or user.username,
            "email": user.email,
            "phone": "",
        },
    )

    if request.method == "POST" and request.POST.get("action") == "update_profile":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        customer.name = name
        customer.email = email
        customer.phone = phone
        customer.address = address
        customer.save()

        user.first_name = name
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")

    recent_bookings = Booking.objects.filter(customer=customer).order_by("-id")[:3]

    return render(
        request,
        "accounts/profile.html",
        {
            "customer": customer,
            "recent_bookings": recent_bookings,
        },
    )


@customer_login_required
def my_bookings(request):
    user = getattr(request, "customer_user", None) or request.user
    customer, _ = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": user.first_name or user.username,
            "email": user.email,
            "phone": "",
        },
    )
    bookings = Booking.objects.filter(customer=customer).order_by("-id")

    return render(
        request,
        "accounts/my_bookings.html",
        {
            "bookings": bookings,
        },
    )


@customer_login_required
def change_password(request):
    user = getattr(request, "customer_user", None) or request.user
    if request.method == "POST":
        old_password = request.POST.get("old_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not user.check_password(old_password):
            messages.error(request, "Current password is incorrect!")
            return redirect("accounts:profile")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match!")
            return redirect("accounts:profile")

        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters!")
            return redirect("accounts:profile")

        user.set_password(new_password)
        user.save()
        update_customer_session_hash(request, user)
        messages.success(request, "Password changed successfully!")

    return redirect("accounts:profile")