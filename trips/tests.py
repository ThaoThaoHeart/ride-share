from django.contrib.gis.geos import Point
from django.test import TestCase

from accounts.models import User
from drivers.models import Driver
from trips.models import Trip
from trips.services import InvalidTripTransition, request_trip, transition_trip

PICKUP = Point(-73.9776, 40.7527, srid=4326)
DROPOFF = Point(-73.9654, 40.7829, srid=4326)


def create_rider(username="rider"):
    return User.objects.create_user(
        username=username,
        password="testpass123",
        role=User.Role.RIDER,
    )


def create_driver(username, point, is_available=True):
    user = User.objects.create_user(
        username=username,
        password="testpass123",
        role=User.Role.DRIVER,
    )
    return Driver.objects.create(user=user, is_available=is_available, location=point)


class RequestTripTests(TestCase):
    def test_stays_requested_when_no_driver_is_nearby(self):
        trip = request_trip(create_rider(), PICKUP, DROPOFF)
        self.assertEqual(trip.status, Trip.Status.REQUESTED)
        self.assertIsNone(trip.driver)

    def test_matches_the_closest_available_driver(self):
        create_driver("farther", Point(-73.9600, 40.7600, srid=4326))
        closer = create_driver("closer", Point(-73.9770, 40.7530, srid=4326))
        trip = request_trip(create_rider(), PICKUP, DROPOFF)
        self.assertEqual(trip.status, Trip.Status.MATCHED)
        self.assertEqual(trip.driver, closer)

    def test_matched_driver_becomes_unavailable(self):
        closer = create_driver("closer", Point(-73.9770, 40.7530, srid=4326))
        request_trip(create_rider(), PICKUP, DROPOFF)
        closer.refresh_from_db()
        self.assertFalse(closer.is_available)


class TransitionTripTests(TestCase):
    def create_trip(self, status):
        return Trip.objects.create(
            rider=create_rider(),
            status=status,
            pickup_location=PICKUP,
            dropoff_location=DROPOFF,
        )

    def test_moves_matched_trip_to_driver_arriving(self):
        trip = self.create_trip(Trip.Status.MATCHED)
        transition_trip(trip, Trip.Status.DRIVER_ARRIVING)
        trip.refresh_from_db()
        self.assertEqual(trip.status, Trip.Status.DRIVER_ARRIVING)

    def test_rejects_skipping_a_status(self):
        trip = self.create_trip(Trip.Status.REQUESTED)
        with self.assertRaises(InvalidTripTransition):
            transition_trip(trip, Trip.Status.COMPLETED)

    def test_rejects_changes_after_completion(self):
        trip = self.create_trip(Trip.Status.COMPLETED)
        with self.assertRaises(InvalidTripTransition):
            transition_trip(trip, Trip.Status.CANCELLED)

    def test_allows_cancelling_before_pickup(self):
        trip = self.create_trip(Trip.Status.MATCHED)
        transition_trip(trip, Trip.Status.CANCELLED)
        trip.refresh_from_db()
        self.assertEqual(trip.status, Trip.Status.CANCELLED)
        