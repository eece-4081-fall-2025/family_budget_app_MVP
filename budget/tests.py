from django.test import TestCase, Client
from django.urls import reverse
import os, json

class UserDataStorageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        # Clean up any test data files created during tests
        for file in os.listdir('.'):
            if file.endswith('_data.json'):
                os.remove(file)

    def _login(self, username):
        # Simulate login (POST to login view)
        resp = self.client.post(reverse("login"), {"username": username})
        self.assertEqual(resp.status_code, 302)  # redirect to dashboard

    def _read_json(self, filename):
        with open(filename, "r") as f:
            return json.load(f)

    def test_data_is_separate_per_user(self):
        # Log in as Aryan and add income
        self._login("Aryan")
        self.client.post(reverse("add_income"), {"source": "Job", "amount": "100"})
        aryan_data = self._read_json("Aryan_data.json")
        self.assertEqual(aryan_data["total_income"], 100)

        # Log in as Jamie and add income
        self._login("Jamie")
        self.client.post(reverse("add_income"), {"source": "Gift", "amount": "200"})
        jamie_data = self._read_json("Jamie_data.json")
        self.assertEqual(jamie_data["total_income"], 200)

        # Recheck Aryan’s data (should remain unchanged)
        aryan_data = self._read_json("Aryan_data.json")
        self.assertEqual(aryan_data["total_income"], 100)
