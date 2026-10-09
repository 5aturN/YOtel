"""Integration tests for the initial room booking API."""

import unittest

from fastapi.testclient import TestClient

from yaotel.api import create_app
from yaotel.config import Settings


class BookingApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(
            Settings(database_url="sqlite+pysqlite:///:memory:", api_key="test-api-key")
        )
        self.client = TestClient(self.app)
        self.headers = {"X-API-Key": "test-api-key"}

    def tearDown(self) -> None:
        self.client.close()
        self.app.state.engine.dispose()

    def test_api_requires_key(self) -> None:
        response = self.client.get(
            "/api/rooms/availability",
            params={"check_in": "2030-01-04", "check_out": "2030-01-07", "guests": 2},
        )
        self.assertEqual(response.status_code, 401)

    def test_booking_creation_blocks_overlapping_dates(self) -> None:
        payload = {
            "room_id": 1,
            "guest_email": "guest@example.com",
            "check_in": "2030-01-04",
            "check_out": "2030-01-07",
            "guests": 2,
        }
        response = self.client.post("/api/bookings", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "pending")
        self.assertEqual(response.json()["total_price_kopecks"], 2_805_000)

        conflict = self.client.post("/api/bookings", json=payload, headers=self.headers)
        self.assertEqual(conflict.status_code, 409)

    def test_invalid_stay_is_rejected(self) -> None:
        response = self.client.get(
            "/api/rooms/availability",
            params={"check_in": "2030-01-07", "check_out": "2030-01-04", "guests": 2},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
