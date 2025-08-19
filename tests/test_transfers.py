"""
Тесты для эндпоинтов переводов.
"""

import pytest
from fastapi import status


class TestTransferEndpoints:
	"""Тесты для эндпоинтов переводов."""

	def test_transfer_success(self, client):
		"""Тест успешного перевода денег."""
		# Получаем начальные балансы
		users_response = client.get("/api/v1/users")
		initial_users = users_response.json()
		initial_balances = {user["id"]: user["balance"] for user in initial_users}
		amount = 50
		transfer_data = {
			"from_user_id": 1,
			"to_user_id": 2,
			"amount": amount
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		assert response.status_code == status.HTTP_200_OK
		data = response.json()
		assert data["from_user_id"] == transfer_data["from_user_id"]
		assert data["to_user_id"] == transfer_data["to_user_id"]
		assert data["amount"] == transfer_data["amount"]
		assert "from_user_balance" in data
		assert "to_user_balance" in data
		assert "message" in data
		
		# Проверяем что в ответе указаны правильные балансы
		assert data["from_user_balance"] == initial_balances[1] - amount
		assert data["to_user_balance"] == initial_balances[2] + amount
		
		# Проверяем что балансы действительно изменились в системе
		users_response = client.get("/api/v1/users")
		final_users = users_response.json()
		final_balances = {user["id"]: user["balance"] for user in final_users}
		
		# Проверяем изменения балансов
		assert final_balances[1] == initial_balances[1] - amount  # Алиса: 100 -> 50
		assert final_balances[2] == initial_balances[2] + amount  # Боб: 250 -> 300
		
		# Проверяем что общая сумма не изменилась
		total_before = sum(initial_balances.values())
		total_after = sum(final_balances.values())
		assert total_before == total_after, "Общая сумма изменилась после перевода"
		
		# Проверяем что в ответе перевода указаны те же значения
		assert data["from_user_balance"] == final_balances[1]
		assert data["to_user_balance"] == final_balances[2]

	def test_transfer_user_not_found(self, client):
		"""Тест перевода с несуществующим пользователем."""
		transfer_data = {
			"from_user_id": 999,  # Несуществующий ID
			"to_user_id": 2,
			"amount": 50
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		assert response.status_code == status.HTTP_404_NOT_FOUND
		assert "Пользователь не найден" in response.json()["detail"]

	def test_transfer_self_transfer(self, client):
		"""Тест попытки перевода самому себе."""
		transfer_data = {
			"from_user_id": 1,
			"to_user_id": 1,  # Тот же пользователь
			"amount": 50
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert "Нельзя переводить деньги самому себе" in response.json()["detail"]

	def test_transfer_insufficient_funds(self, client):
		"""Тест перевода при недостатке средств."""
		transfer_data = {
			"from_user_id": 1,  # У Алисы баланс 100
			"to_user_id": 2,
			"amount": 150  # Больше чем есть
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert "Недостаточно средств" in response.json()["detail"]

	def test_transfer_invalid_amount_zero(self, client):
		"""Тест перевода с нулевой суммой."""
		transfer_data = {
			"from_user_id": 1,
			"to_user_id": 2,
			"amount": 0
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		# Pydantic валидация возвращает 422 для некорректных данных
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_transfer_invalid_amount_negative(self, client):
		"""Тест перевода с отрицательной суммой."""
		transfer_data = {
			"from_user_id": 1,
			"to_user_id": 2,
			"amount": -10
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		# Pydantic валидация возвращает 422 для некорректных данных
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_transfer_missing_required_fields(self, client):
		"""Тест перевода без обязательных полей."""
		# Без from_user_id
		response = client.post("/api/v1/transfer", json={
			"to_user_id": 2,
			"amount": 50
		})
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
		
		# Без to_user_id
		response = client.post("/api/v1/transfer", json={
			"from_user_id": 1,
			"amount": 50
		})
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
		
		# Без amount
		response = client.post("/api/v1/transfer", json={
			"from_user_id": 1,
			"to_user_id": 2
		})
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_transfer_invalid_user_id_types(self, client):
		"""Тест перевода с неверными типами ID пользователей."""
		transfer_data = {
			"from_user_id": "invalid",  # Должен быть int
			"to_user_id": 2,
			"amount": 50
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_transfer_invalid_amount_type(self, client):
		"""Тест перевода с неверным типом суммы."""
		transfer_data = {
			"from_user_id": 1,
			"to_user_id": 2,
			"amount": "invalid"  # Должен быть int
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

	def test_transfer_transaction_rollback(self, client):
		"""Тест отката транзакции при ошибке."""
		# Получаем начальные балансы
		users_response = client.get("/api/v1/users")
		initial_users = users_response.json()
		initial_balances = {user["id"]: user["balance"] for user in initial_users}
		
		# Пытаемся выполнить перевод с ошибкой
		transfer_data = {
			"from_user_id": 1,
			"to_user_id": 2,
			"amount": 1000  # Больше чем есть у Алисы
		}
		
		response = client.post("/api/v1/transfer", json=transfer_data)
		
		# Проверяем что получили ошибку
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		
		# Проверяем что балансы не изменились
		users_response = client.get("/api/v1/users")
		final_users = users_response.json()
		final_balances = {user["id"]: user["balance"] for user in final_users}
		
		# Балансы должны остаться неизменными
		assert initial_balances == final_balances, "Транзакция не была откачена"
