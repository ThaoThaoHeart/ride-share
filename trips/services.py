from django.db import transaction

from drivers.services import nearby_drivers
from trips.models import Trip

MATCH_RADIUS_KM = 3

ALLOWED_TRANSITIONS = {
    Trip.Status.REQUESTED: {Trip.Status.MATCHED, Trip.Status.CANCELLED},
    Trip.Status.MATCHED: {Trip.Status.DRIVER_ARRIVING, Trip.Status.CANCELLED},
    Trip.Status.DRIVER_ARRIVING: {Trip.Status.IN_PROGRESS, Trip.Status.CANCELLED},
    Trip.Status.IN_PROGRESS: {Trip.Status.COMPLETED},
    Trip.Status.COMPLETED: set(),
    Trip.Status.CANCELLED: set(),
}


class InvalidTripTransition(Exception):
    pass


def request_trip(rider, pickup_location, dropoff_location):
    trip = Trip.objects.create(
        rider=rider,
        pickup_location=pickup_location,
        dropoff_location=dropoff_location,
    )
    return match_trip(trip)


def match_trip(trip):
    with transaction.atomic():
        driver = (
            nearby_drivers(trip.pickup_location, km=MATCH_RADIUS_KM)
            .select_for_update()
            .first()
        )
        if driver is None:
            return trip

        driver.is_available = False
        driver.save(update_fields=["is_available"])
        trip.driver = driver
        trip.status = Trip.Status.MATCHED
        trip.save(update_fields=["driver", "status", "updated_at"])
    return trip


def transition_trip(trip, new_status):
    current_status = Trip.Status(trip.status)
    target_status = Trip.Status(new_status)
    if target_status not in ALLOWED_TRANSITIONS[current_status]:
        raise InvalidTripTransition(
            f"Cannot move trip from {current_status.value} to {target_status.value}"
        )
    trip.status = target_status
    trip.save(update_fields=["status", "updated_at"])
    return trip
    