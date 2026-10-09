"""Smoke-test состояния приложения."""

import unittest

from fastapi.testclient import TestClient

from yaotel.main import app


class HealthEndpointTests(unittest.TestCase):
    def test_health_returns_ok(self) -> None:
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
