from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

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
    