"""Validated request and response models for the initial booking API."""

import re
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BookingCreate(BaseModel):
    room_id: int = Field(gt=0)
    guest_email: str = Field(min_length=3, max_length=254)
    check_in: date
    check_out: date
    guests: int = Field(ge=1, le=10)

    @field_validator("guest_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("A valid email address is required.")
        return normalized

    @model_validator(mode="after")
    def validate_stay(self) -> "BookingCreate":
        if self.check_out <= self.check_in:
            raise ValueError("Check-out date must be later than check-in date.")
        return self


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    category: str
    capacity: int
    base_price_kopecks: int
    status: str


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    room_id: int
    guest_email: str
    check_in: date
    check_out: date
    guests: int
    total_price_kopecks: int
    status: str
