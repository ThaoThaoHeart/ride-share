from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.utils import timezone

from .models import Driver


def nearby_drivers(point, km=3):
    return (
        Driver.objects.filter(
            is_available=True,
            location__distance_lte=(point, D(km=km)),
        )
        .annotate(distance=Distance("location", point))
        .order_by("distance")
    )
    
def update_driver_location(user, latitude, longitude):
    driver, _ = Driver.objects.get_or_create(user=user)
    driver.location = Point(longitude, latitude, srid=4326)
    driver.location_updated_at = timezone.now()
    driver.save(update_fields=["location", "location_updated_at"])
    return driver
    