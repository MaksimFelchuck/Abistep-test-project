"""
Тесты для основных эндпоинтов приложения.
"""

import pytest
from fastapi import status


class TestMainEndpoints:
	"""Тесты для основных эндпоинтов."""

	def test_read_root(self, client):
		"""Тест корневого эндпоинта."""
		response = client.get("/")
		
		assert response.status_code == status.HTTP_200_OK
		data = response.json()
		assert "name" in data
		assert "version" in data
		assert data["name"] == "Abistep Test Project"
		assert data["version"] == "0.1.0"

	def test_health(self, client):
		"""Тест health check эндпоинта."""
		response = client.get("/health")
		
		assert response.status_code == status.HTTP_200_OK
		data = response.json()
		assert "status" in data
		assert data["status"] == "ok"

	def test_openapi_schema(self, client):
		"""Тест доступности OpenAPI схемы."""
		response = client.get("/openapi.json")
		
		assert response.status_code == status.HTTP_200_OK
		data = response.json()
		assert "openapi" in data
		assert "info" in data
		assert "paths" in data
		assert data["info"]["title"] == "Abistep Test Project"
		assert data["info"]["version"] == "0.1.0"

	def test_docs_endpoint(self, client):
		"""Тест доступности Swagger UI."""
		response = client.get("/docs")
		
		assert response.status_code == status.HTTP_200_OK
		assert "text/html" in response.headers["content-type"]

	def test_redoc_endpoint(self, client):
		"""Тест доступности ReDoc."""
		response = client.get("/redoc")
		
		assert response.status_code == status.HTTP_200_OK
		assert "text/html" in response.headers["content-type"]
