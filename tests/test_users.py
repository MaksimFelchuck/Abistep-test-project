"""
Тесты для эндпоинтов пользователей.
"""

import pytest
from fastapi import status


class TestUsersEndpoints:
	"""Тесты для эндпоинтов пользователей."""

	def test_create_user_success(self, client):
		"""Тест успешного создания пользователя."""
		user_data = {
			"name": "Тест",
			"email": "test@example.com",
			"balance": 500
		}
		
		response = client.post("/api/v1/users", json=user_data)
		
		assert response.status_code == status.HTTP_201_CREATED
		data = response.json()
		assert data["name"] == user_data["name"]
		assert data["email"] == user_data["email"]
		assert data["balance"] == user_data["balance"]
		assert "id" in data

	def test_create_user_without_balance(self, client):
		"""Тест создания пользователя без указания баланса."""
		user_data = {
			"name": "Тест2",
			"email": "test2@example.com"
		}
		
		response = client.post("/api/v1/users", json=user_data)
		
		assert response.status_code == status.HTTP_201_CREATED
		data = response.json()
		assert data["balance"] == 0  # Стартовый баланс из конфига

	def test_create_user_duplicate_email(self, client):
		"""Тест создания пользователя с существующим email."""
		# Пытаемся создать пользователя с email Алисы (уже существует)
		duplicate_data = {
			"name": "Тест4",
			"email": "alice@example.com",  # Email Алисы уже существует
			"balance": 200
		}
		response = client.post("/api/v1/users", json=duplicate_data)
		
		assert response.status_code == status.HTTP_409_CONFLICT
		assert "Email уже используется" in response.json()["detail"]

	def test_create_user_invalid_email(self, client):
		"""Тест создания пользователя с неверным email."""
		user_data = {
			"name": "Тест5",
			"email": "invalid-email",
			"balance": 100
		}
		
		response = client.post("/api/v1/users", json=user_data)
		
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_create_user_empty_name(self, client):
		"""Тест создания пользователя с пустым именем."""
		user_data = {
			"name": "",
			"email": "test6@example.com",
			"balance": 100
		}
		
		response = client.post("/api/v1/users", json=user_data)
		
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_create_user_missing_required_fields(self, client):
		"""Тест создания пользователя без обязательных полей."""
		# Без имени
		response = client.post("/api/v1/users", json={"email": "test7@example.com"})
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
		
		# Без email
		response = client.post("/api/v1/users", json={"name": "Тест7"})
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_list_users_success(self, client):
		"""Тест успешного получения списка пользователей."""
		response = client.get("/api/v1/users")
		
		assert response.status_code == status.HTTP_200_OK
		data = response.json()
		assert isinstance(data, list)
		assert len(data) >= 2  # Минимум 2 тестовых пользователя (Алиса и Боб)
		
		# Проверяем структуру первого пользователя
		if data:
			user = data[0]
			assert "id" in user
			assert "name" in user
			assert "email" in user
			assert "balance" in user

	def test_list_users_structure(self, client):
		"""Тест получения списка пользователей (проверка структуры ответа)."""
		response = client.get("/api/v1/users")
		
		assert response.status_code == status.HTTP_200_OK
		data = response.json()
		assert isinstance(data, list)
		
		# Проверяем что все пользователи имеют правильную структуру
		for user in data:
			assert isinstance(user["id"], int)
			assert isinstance(user["name"], str)
			assert isinstance(user["email"], str)
			assert isinstance(user["balance"], int)
			assert user["balance"] >= 0

	def test_list_users_contains_test_data(self, client):
		"""Тест что в списке есть тестовые пользователи."""
		response = client.get("/api/v1/users")
		
		assert response.status_code == status.HTTP_200_OK
		data = response.json()
		
		# Проверяем что есть тестовые пользователи
		names = [user["name"] for user in data]
		emails = [user["email"] for user in data]
		
		assert "Алиса" in names
		assert "Боб" in names
		assert "alice@example.com" in emails
		assert "bob@example.com" in emails
