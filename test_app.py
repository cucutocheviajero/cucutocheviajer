# -*- coding: utf-8 -*-

import pytest
from app import app
import time

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    return client

def print_result(name, status, duration, extra=""):
    print(f"[{status}] {name:<30} | Tiempo: {duration:.4f}s {extra}")

# -------------------------------
# PRUEBAS DE RUTAS GENERALES
# -------------------------------

def test_home(client):
    start = time.time()
    response = client.get('/')
    duration = time.time() - start
    status = "OK" if response.status_code == 200 else "FAIL"
    print_result("Ruta '/' (home)", status, duration)
    assert response.status_code == 200

def test_about(client):
    start = time.time()
    response = client.get('/about')
    duration = time.time() - start
    status = "OK" if response.status_code == 200 else "FAIL"
    print_result("Ruta '/about'", status, duration)
    assert response.status_code == 200

def test_contact_get(client):
    start = time.time()
    response = client.get('/contact')
    duration = time.time() - start
    status = "OK" if response.status_code == 200 else "FAIL"
    print_result("Ruta '/contact' (GET)", status, duration)
    assert response.status_code == 200

def test_contact_post_fake(client):
    start = time.time()
    response = client.post('/contact', data={
        'name': 'Prueba',
        'email': 'test@example.com',
        'message': 'Mensaje de prueba'
    }, follow_redirects=True)
    duration = time.time() - start
    status = "OK" if response.status_code == 200 else "FAIL"
    print_result("Ruta '/contact' (POST)", status, duration)
    assert response.status_code == 200

def test_departments(client):
    start = time.time()
    response = client.get('/departments')
    duration = time.time() - start
    status = "OK" if response.status_code == 200 else "FAIL"
    print_result("Ruta '/departments'", status, duration)
    assert response.status_code == 200

# -------------------------------
# PRUEBAS DINÁMICAS – Ejemplos simulados
# -------------------------------

@pytest.mark.parametrize("department", ["Departamento de Bolivar", "Departamento de Casanare", "Departamento de Nariño"])  # Puedes ajustar los nombres
def test_show_department(client, department):
    start = time.time()
    response = client.get(f'/departments/{department}')
    duration = time.time() - start
    status = "OK" if response.status_code in [200, 404] else "FAIL"
    extra = "(404 esperado)" if response.status_code == 404 else ""
    print_result(f"/departments/{department}", status, duration, extra)
    assert response.status_code in [200, 404]

@pytest.mark.parametrize("department,municipality", [
    ("Capitanejo", "Guadalupe"),
    ("Florian", "Vetas")
])  # Simula rutas conocidas
def test_show_places(client, department, municipality):
    start = time.time()
    response = client.get(f'/departments/{department}/{municipality}')
    duration = time.time() - start
    status = "OK" if response.status_code in [200, 404] else "FAIL"
    extra = "(404 esperado)" if response.status_code == 404 else ""
    print_result(f"/departments/{department}/{municipality}", status, duration, extra)
    assert response.status_code in [200, 404]

@pytest.mark.parametrize("municipality_id", [1, 2, 4])
def test_municipality_page(client, municipality_id):
    start = time.time()
    response = client.get(f'/municipality/{municipality_id}')
    duration = time.time() - start
    status = "OK" if response.status_code in [200, 404] else "FAIL"
    extra = "(404 esperado)" if response.status_code == 404 else ""
    print_result(f"/municipality/{municipality_id}", status, duration, extra)
    assert response.status_code in [200, 404]

@pytest.mark.parametrize("place_id", [1, 2, 100])
def test_place_detail(client, place_id):
    start = time.time()
    response = client.get(f'/places/{place_id}')
    duration = time.time() - start
    status = "OK" if response.status_code in [200, 404] else "FAIL"
    extra = "(404 esperado)" if response.status_code == 404 else ""
    print_result(f"/places/{place_id}", status, duration, extra)
    assert response.status_code in [200, 404]

