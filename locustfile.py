# -*- coding: utf-8 -*-

from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Espera de 1 a 3 segundos entre tareas

    # Rutas estáticas
    @task(3)
    def home(self):
        self.client.get("/")

    @task(2)
    def about(self):
        self.client.get("/about")

    @task(2)
    def contact_get(self):
        self.client.get("/contact")

    @task(1)
    def contact_post(self):
        self.client.post("/contact", data={
            "name": "Locust User",
            "email": "locust@example.com",
            "message": "Esto es una prueba automática de estrés con Locust."
        })

    @task(2)
    def departments(self):
        self.client.get("/departments")

    # Rutas dinámicas simuladas (ajusta según tus datos reales si lo deseas)
    departamentos = ["Norte_de_Santander", "Santander", "Casanare"]
    municipios = ["Cucuta", "Pamplona", "Bucaramanga", "Yopal"]
    municipio_ids = [1, 2, 3, 4]
    place_ids = [1, 2, 3, 4, 100]

    @task(1)
    def show_department(self):
        dept = random.choice(self.departamentos)
        self.client.get(f"/departments/{dept}")

    @task(1)
    def show_places(self):
        dept = random.choice(self.departamentos)
        muni = random.choice(self.municipios)
        self.client.get(f"/departments/{dept}/{muni}")

    @task(1)
    def municipality_page(self):
        muni_id = random.choice(self.municipio_ids)
        self.client.get(f"/municipality/{muni_id}")

    @task(1)
    def place_detail(self):
        place_id = random.choice(self.place_ids)
        self.client.get(f"/places/{place_id}")
