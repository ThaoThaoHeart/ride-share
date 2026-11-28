from django.conf import settings
from django.contrib.gis.db import models


class Trip(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        MATCHED = "matched", "Matched"
        DRIVER_ARRIVING = "driver_arriving", "Driver arriving"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trips_as_rider",
    )
    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trips",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
    )
    pickup_location = models.PointField(geography=True, srid=4326)
    dropoff_location = models.PointField(geography=True, srid=4326)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trip {self.id} - {self.status}"
    