from django.urls import path
from . import views

urlpatterns = [
    path("", views.halls_list, name="halls_list"),
    path("<slug:slug>/", views.hall_detail, name="hall_detail"),
]