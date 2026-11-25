from django.conf import settings
from django.contrib.gis.db import models


class Driver(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver",
    )
    is_available = models.BooleanField(default=False)
    location = models.PointField(geography=True, srid=4326, null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username
