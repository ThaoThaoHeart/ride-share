from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import User
from drivers.models import Driver
from drivers.services import nearby_drivers

GRAND_CENTRAL = Point(-73.9776, 40.7527, srid=4326)


def create_driver(username, point, is_available=True):
    user = User.objects.create_user(
        username=username,
        password="testpass123",
        role=User.Role.DRIVER,
    )
    return Driver.objects.create(user=user, is_available=is_available, location=point)


class NearbyDriversTests(TestCase):
    def test_returns_nearby_available_driver(self):
        nearby = create_driver("near", Point(-73.9857, 40.7484, srid=4326))
        self.assertIn(nearby, nearby_drivers(GRAND_CENTRAL, km=3))

    def test_excludes_drivers_beyond_radius(self):
        far = create_driver("far", Point(-71.0589, 42.3601, srid=4326))
        self.assertNotIn(far, nearby_drivers(GRAND_CENTRAL, km=3))

    def test_excludes_unavailable_drivers(self):
        busy = create_driver("busy", Point(-73.9857, 40.7484, srid=4326), is_available=False)
        self.assertNotIn(busy, nearby_drivers(GRAND_CENTRAL, km=3))

    def test_orders_closest_first(self):
        farther = create_driver("farther", Point(-73.9600, 40.7600, srid=4326))
        closer = create_driver("closer", Point(-73.9770, 40.7530, srid=4326))
        self.assertEqual(list(nearby_drivers(GRAND_CENTRAL, km=3)), [closer, farther])


class DriverLocationViewTests(APITestCase):
    def setUp(self):
        self.driver_user = User.objects.create_user(
            username="driver",
            password="testpass123",
            role=User.Role.DRIVER,
        )
        self.rider_user = User.objects.create_user(
            username="rider",
            password="testpass123",
            role=User.Role.RIDER,
        )
        self.url = reverse("driver-location")

    def test_driver_can_update_location(self):
        self.client.force_authenticate(self.driver_user)
        response = self.client.post(
            self.url,
            {"latitude": 40.7484, "longitude": -73.9857},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(Driver.objects.get(user=self.driver_user).location)

    def test_rider_cannot_update_location(self):
        self.client.force_authenticate(self.rider_user)
        response = self.client.post(
            self.url,
            {"latitude": 40.7484, "longitude": -73.9857},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_rejects_out_of_range_latitude(self):
        self.client.force_authenticate(self.driver_user)
        response = self.client.post(
            self.url,
            {"latitude": 200, "longitude": 0},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        