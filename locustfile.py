from locust import HttpUser, task, between
import random

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def create_order(self):
        order_data = {
            "user_id": random.randint(1, 100),
            "items": [
                {
                    "product_id": random.randint(1, 50),
                    "quantity": random.randint(1, 3)
                }
            ]
        }
        with self.client.post("/orders/", json=order_data, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(f"Create order failed: {response.text}")

    @task(2)
    def update_order_status(self):
        order_id = random.randint(1, 200)
        with self.client.patch(
            f"/orders/{order_id}",
            json={"prep_status": "ready", "delivery_status": "out_for_delivery"},
            catch_response=True
        ) as response:
            if response.status_code not in (200, 404):
                response.failure(f"Update order failed: {response.text}")

    @task(1)
    def get_orders(self):
        with self.client.get("/orders/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Get orders failed: {response.text}")

    @task(1)
    def get_products(self):
        with self.client.get("/products/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Get products failed: {response.text}")

    @task(1)
    def get_users(self):
        with self.client.get("/user/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Get users failed: {response.text}")