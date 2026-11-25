from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from .models import Driver
from .serializers import LocationUpdateSerializer


class DriverLocationView(APIView):
    def post(self, request):
        if request.user.role != User.Role.DRIVER:
            return Response(
                {"detail": "Only drivers can update location."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        driver, _ = Driver.objects.get_or_create(user=request.user)
        driver.location = Point(data["longitude"], data["latitude"], srid=4326)
        driver.location_updated_at = timezone.now()
        driver.save(update_fields=["location", "location_updated_at"])
        return Response({"status": "ok"})
        