from locust import HttpUser, task, between
import random
from bs4 import BeautifulSoup


class ClinicUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        response = self.client.get("/")
        if response.status_code == 200:
            users = response.json().get("users", [])
            if users:
                self.test_users = users
            else:
                self.test_users = [{"email": "invalid@example.com", "password": "wrong"}]
        else:
            self.test_users = [{"email": "invalid@example.com", "password": "wrong"}]

    @task
    def login(self):
        user = random.choice(self.test_users)

        # Get login page first to establish session (and fetch CSRF if needed)
        self.client.get("/")
        
        login_data = {
            "email": user["email"],
            "password": user["password"],
        }

        with self.client.post("/", data=login_data, allow_redirects=True, catch_response=True) as res:
            if "dashboard" in res.text.lower() or "Logged in successfully" in res.text:
                res.success()
            else:
                res.failure(f"Login failed for {user['email']}")
