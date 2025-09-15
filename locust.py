from locust import HttpUser, task, between


class ClinicUser(HttpUser):
    wait_time = between(1, 5)  

    BASE_EMAIL = "patient{}@gmail.com"
    PASSWORD = "patient"
    USER_COUNT = 50  

    @task(1)
    def login(self):
        user_index = self.user_index % self.USER_COUNT + 1
        email = self.BASE_EMAIL.format(user_index)
        password = f"{self.PASSWORD}{user_index}"


        self.client.post("/login", json={
            "email": email,
            "password": password
            })

    @task(2)
    def appoint(self):
        self.client.post("/create_appointment", json={ "preferred_date" : "2025-12-31" })
        self.client.post("/create_appointment", json={ "preferred_time" : " 10:00" }),
        self.client.post("/create_appointment", json={ "doctor_id" : 1 }),
        self.client.post("/create_appointment", json={ "patient_id" : 1 }),
        self.client.post("/create_appointment", json={ "status" : "Pending" })

