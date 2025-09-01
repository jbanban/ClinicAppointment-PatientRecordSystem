from locust import HttpUser, task, between
from bs4 import BeautifulSoup


class ClinicUser(HttpUser):
    wait_time = between(1, 5)  # Simulate user waiting 1-5 seconds between tasks

    def on_start(self):
        # Replace these credentials with a real test user from your database
        self.email = "test_patient@example.com"
        self.password = "testpassword"

    @task
    def login(self):
        # Step 1: Get the login page to fetch CSRF tokens or session cookies if needed
        response = self.client.get("/")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract CSRF token if applicable (Flask-WTF or custom)
        # csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

        # Step 2: POST login data
        login_data = {
            "email": self.email,
            "password": self.password,
            # "csrf_token": csrf_token,  # Uncomment if you use CSRF protection
        }

        with self.client.post("/", data=login_data, allow_redirects=True, catch_response=True) as res:
            if "dashboard" in res.text.lower() or "Logged in successfully" in res.text:
                res.success()
            else:
                res.failure("Login failed or dashboard not loaded")


