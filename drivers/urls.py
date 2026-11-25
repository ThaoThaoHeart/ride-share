from django.urls import path

from . import views

urlpatterns = [
    path("location/", views.DriverLocationView.as_view(), name="driver-location"),
]
