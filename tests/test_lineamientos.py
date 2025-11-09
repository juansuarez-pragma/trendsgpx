"""
Tests para CRUD de Lineamientos
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


class TestLineamientosCRUD:
    """Tests para endpoints CRUD de lineamientos"""

    def test_create_lineamiento_success(self, client: TestClient, auth_headers: dict):
        """Test crear lineamiento exitosamente"""
        payload = {
            "nombre": "Tecnología IA 2025",
            "keywords": ["IA", "inteligencia artificial", "machine learning"],
            "plataformas": ["youtube", "reddit"],
        }

        response = client.post("/lineamientos/", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()

        assert data["nombre"] == payload["nombre"]
        assert set(data["keywords"]) == set(payload["keywords"])
        assert set(data["plataformas"]) == set(payload["plataformas"])
        assert data["activo"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_lineamiento_missing_auth(self, client: TestClient):
        """Test crear lineamiento sin autenticación"""
        payload = {
            "nombre": "Test",
            "keywords": ["test"],
            "plataformas": ["youtube"],
        }

        response = client.post("/lineamientos/", json=payload)

        assert response.status_code == 401

    def test_create_lineamiento_invalid_platform(self, client: TestClient, auth_headers: dict):
        """Test crear lineamiento con plataforma inválida"""
        payload = {
            "nombre": "Test",
            "keywords": ["test"],
            "plataformas": ["tiktok"],  # Plataforma no soportada
        }

        response = client.post("/lineamientos/", json=payload, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    def test_create_lineamiento_duplicate_name(self, client: TestClient, auth_headers: dict):
        """Test crear lineamiento con nombre duplicado"""
        payload = {
            "nombre": "Tecnología Única",
            "keywords": ["tech"],
            "plataformas": ["youtube"],
        }

        # Crear primero
        response1 = client.post("/lineamientos/", json=payload, headers=auth_headers)
        assert response1.status_code == 201

        # Intentar crear duplicado
        response2 = client.post("/lineamientos/", json=payload, headers=auth_headers)
        assert response2.status_code == 400
        assert "Ya existe" in response2.json()["detail"]

    def test_create_lineamiento_empty_keywords(self, client: TestClient, auth_headers: dict):
        """Test crear lineamiento con keywords vacío"""
        payload = {
            "nombre": "Test",
            "keywords": [],
            "plataformas": ["youtube"],
        }

        response = client.post("/lineamientos/", json=payload, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    def test_list_lineamientos_empty(self, client: TestClient, auth_headers: dict):
        """Test listar lineamientos cuando no hay ninguno"""
        response = client.get("/lineamientos/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 0
        assert data["items"] == []

    def test_list_lineamientos_with_data(self, client: TestClient, auth_headers: dict):
        """Test listar lineamientos con datos"""
        # Crear 3 lineamientos
        for i in range(3):
            payload = {
                "nombre": f"Lineamiento {i}",
                "keywords": [f"keyword{i}"],
                "plataformas": ["youtube"],
            }
            client.post("/lineamientos/", json=payload, headers=auth_headers)

        # Listar
        response = client.get("/lineamientos/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_lineamientos_pagination(self, client: TestClient, auth_headers: dict):
        """Test paginación de lineamientos"""
        # Crear 5 lineamientos
        for i in range(5):
            payload = {
                "nombre": f"Lineamiento {i}",
                "keywords": [f"keyword{i}"],
                "plataformas": ["youtube"],
            }
            client.post("/lineamientos/", json=payload, headers=auth_headers)

        # Listar con skip=2, limit=2
        response = client.get(
            "/lineamientos/?skip=2&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 5
        assert len(data["items"]) == 2

    def test_get_lineamiento_by_id(self, client: TestClient, auth_headers: dict):
        """Test obtener lineamiento por ID"""
        # Crear lineamiento
        payload = {
            "nombre": "Test Lineamiento",
            "keywords": ["test"],
            "plataformas": ["youtube"],
        }
        create_response = client.post("/lineamientos/", json=payload, headers=auth_headers)
        lineamiento_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(f"/lineamientos/{lineamiento_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == lineamiento_id
        assert data["nombre"] == payload["nombre"]

    def test_get_lineamiento_not_found(self, client: TestClient, auth_headers: dict):
        """Test obtener lineamiento que no existe"""
        fake_id = str(uuid4())
        response = client.get(f"/lineamientos/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_update_lineamiento_success(self, client: TestClient, auth_headers: dict):
        """Test actualizar lineamiento exitosamente"""
        # Crear lineamiento
        payload = {
            "nombre": "Original",
            "keywords": ["original"],
            "plataformas": ["youtube"],
        }
        create_response = client.post("/lineamientos/", json=payload, headers=auth_headers)
        lineamiento_id = create_response.json()["id"]

        # Actualizar
        update_payload = {
            "nombre": "Actualizado",
            "keywords": ["actualizado", "nuevo"],
        }
        response = client.put(
            f"/lineamientos/{lineamiento_id}",
            json=update_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["nombre"] == "Actualizado"
        assert set(data["keywords"]) == {"actualizado", "nuevo"}
        assert data["plataformas"] == ["youtube"]  # No cambió

    def test_update_lineamiento_partial(self, client: TestClient, auth_headers: dict):
        """Test actualización parcial de lineamiento"""
        # Crear lineamiento
        payload = {
            "nombre": "Original",
            "keywords": ["original"],
            "plataformas": ["youtube"],
        }
        create_response = client.post("/lineamientos/", json=payload, headers=auth_headers)
        lineamiento_id = create_response.json()["id"]

        # Actualizar solo activo
        update_payload = {"activo": False}
        response = client.put(
            f"/lineamientos/{lineamiento_id}",
            json=update_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["activo"] is False
        assert data["nombre"] == "Original"  # No cambió

    def test_update_lineamiento_not_found(self, client: TestClient, auth_headers: dict):
        """Test actualizar lineamiento que no existe"""
        fake_id = str(uuid4())
        update_payload = {"nombre": "Test"}

        response = client.put(
            f"/lineamientos/{fake_id}",
            json=update_payload,
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_delete_lineamiento_soft(self, client: TestClient, auth_headers: dict):
        """Test soft delete de lineamiento"""
        # Crear lineamiento
        payload = {
            "nombre": "Para Eliminar",
            "keywords": ["test"],
            "plataformas": ["youtube"],
        }
        create_response = client.post("/lineamientos/", json=payload, headers=auth_headers)
        lineamiento_id = create_response.json()["id"]

        # Eliminar (soft delete)
        response = client.delete(f"/lineamientos/{lineamiento_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verificar que está marcado como inactivo
        get_response = client.get(f"/lineamientos/{lineamiento_id}", headers=auth_headers)
        assert get_response.status_code == 200
        assert get_response.json()["activo"] is False

    def test_activate_lineamiento(self, client: TestClient, auth_headers: dict):
        """Test reactivar lineamiento"""
        # Crear y eliminar lineamiento
        payload = {
            "nombre": "Para Reactivar",
            "keywords": ["test"],
            "plataformas": ["youtube"],
        }
        create_response = client.post("/lineamientos/", json=payload, headers=auth_headers)
        lineamiento_id = create_response.json()["id"]

        client.delete(f"/lineamientos/{lineamiento_id}", headers=auth_headers)

        # Reactivar
        response = client.post(
            f"/lineamientos/{lineamiento_id}/activate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["activo"] is True

    def test_list_lineamientos_activo_only(self, client: TestClient, auth_headers: dict):
        """Test listar solo lineamientos activos"""
        # Crear 2 lineamientos activos
        for i in range(2):
            payload = {
                "nombre": f"Activo {i}",
                "keywords": ["test"],
                "plataformas": ["youtube"],
            }
            client.post("/lineamientos/", json=payload, headers=auth_headers)

        # Crear 1 y desactivar
        payload = {
            "nombre": "Inactivo",
            "keywords": ["test"],
            "plataformas": ["youtube"],
        }
        create_response = client.post("/lineamientos/", json=payload, headers=auth_headers)
        lineamiento_id = create_response.json()["id"]
        client.delete(f"/lineamientos/{lineamiento_id}", headers=auth_headers)

        # Listar solo activos
        response = client.get("/lineamientos/?activo_only=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 2
        assert all(item["activo"] for item in data["items"])
