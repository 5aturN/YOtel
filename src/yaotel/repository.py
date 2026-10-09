"""Data access for rooms and bookings."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from yaotel.models import Booking, Room

ACTIVE_BOOKING_STATUSES = ("pending", "confirmed", "checked_in")
READY_ROOM_STATUSES = ("clean", "inspected")


def list_available_rooms(
    session: Session, check_in: date, check_out: date, guests: int
) -> list[Room]:
    """Return ready rooms with enough capacity and no overlapping active booking."""
    overlapping_booking = (
        select(Booking.id)
        .where(
            Booking.room_id == Room.id,
            Booking.status.in_(ACTIVE_BOOKING_STATUSES),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
        .exists()
    )
    statement = (
        select(Room)
        .where(
            Room.capacity >= guests,
            Room.status.in_(READY_ROOM_STATUSES),
            ~overlapping_booking,
        )
        .order_by(Room.number)
    )
    return list(session.scalars(statement))


def get_room_for_booking(session: Session, room_id: int) -> Room | None:
    """Lock the selected room row while a booking is being validated and inserted."""
    return session.scalar(select(Room).where(Room.id == room_id).with_for_update())


def booking_overlaps(
    session: Session, room_id: int, check_in: date, check_out: date
) -> bool:
    statement = select(Booking.id).where(
        Booking.room_id == room_id,
        Booking.status.in_(ACTIVE_BOOKING_STATUSES),
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    )
    return session.scalar(statement.limit(1)) is not None
