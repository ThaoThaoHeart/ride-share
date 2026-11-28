from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LocationUpdateSerializer
from .services import update_driver_location


class DriverLocationView(APIView):
    def post(self, request):
        if request.user.role != request.user.Role.DRIVER:
            return Response(
                {"detail": "Only drivers can update location."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_driver_location(
            user=request.user,
            latitude=serializer.validated_data["latitude"],
            longitude=serializer.validated_data["longitude"],
        )
        return Response({"status": "ok"})
        