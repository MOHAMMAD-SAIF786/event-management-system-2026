from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="user_logout"),
    path("logout/alias/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("change-password/", views.change_password, name="change_password"),
]