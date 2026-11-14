
import unittest

from fastapi.testclient import TestClient

from app.main import app, WEBHOOK_PATH


class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_home(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Bot is running")

    def test_info_endpoint_removed(self):
        response = self.client.get(f"{WEBHOOK_PATH}/info")

        self.assertEqual(response.status_code, 404)

    def test_clear_endpoint_removed(self):
        response = self.client.get(f"{WEBHOOK_PATH}/clear")

        self.assertEqual(response.status_code, 404)

    def test_post_endpoint_removed(self):
        response = self.client.post(
            f"{WEBHOOK_PATH}/post/",
            json={"text": "Test reminder"}
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
