"""
Тесты для репозитория пользователей.
"""

import pytest
from app.repositories.user_repository import InMemoryUserRepository
from app.core.exceptions import (
	UserNotFoundError, SelfTransferError, 
	InsufficientFundsError, InvalidAmountError, EmailAlreadyExistsError
)


class TestUserRepository:
	"""Тесты для репозитория пользователей."""

	def test_init_with_test_data(self, user_repository):
		"""Тест инициализации с тестовыми данными."""
		users = user_repository.list()
		assert len(users) == 2
		
		# Проверяем первого пользователя (Алиса)
		alice = user_repository.get_by_id(1)
		assert alice is not None
		assert alice.name == "Алиса"
		assert alice.email == "alice@example.com"
		assert alice.balance == 100
		
		# Проверяем второго пользователя (Боб)
		bob = user_repository.get_by_id(2)
		assert bob is not None
		assert bob.name == "Боб"
		assert bob.email == "bob@example.com"
		assert bob.balance == 250

	def test_test_data_consistency(self, user_repository):
		"""Тест консистентности тестовых данных."""
		users = user_repository.list()
		
		# Проверяем что ID последовательные
		ids = [user.id for user in users]
		assert ids == [1, 2]
		
		# Проверяем что email уникальные
		emails = [user.email for user in users]
		assert len(emails) == len(set(emails))
		
		# Проверяем что балансы корректные
		for user in users:
			assert user.balance >= 0
			assert isinstance(user.balance, int)

	def test_create_user_success(self, user_repository):
		"""Тест успешного создания пользователя."""
		initial_count = len(user_repository.list())
		
		user = user_repository.create("Тест", "test@example.com", 500)
		
		assert user.id == 3  # Следующий ID после тестовых пользователей
		assert user.name == "Тест"
		assert user.email == "test@example.com"
		assert user.balance == 500
		
		# Проверяем что пользователь добавлен в список
		final_count = len(user_repository.list())
		assert final_count == initial_count + 1
		
		# Проверяем что можно найти по email
		found_user = user_repository.get_by_email("test@example.com")
		assert found_user is not None
		assert found_user.id == user.id

	def test_create_user_duplicate_email(self, user_repository):
		"""Тест создания пользователя с существующим email."""
		# Создаем первого пользователя
		user_repository.create("Тест1", "duplicate@example.com", 100)
		
		# Пытаемся создать второго с тем же email
		with pytest.raises(EmailAlreadyExistsError):
			user_repository.create("Тест2", "duplicate@example.com", 200)

	def test_create_user_duplicate_test_email(self, user_repository):
		"""Тест создания пользователя с email тестовых пользователей."""
		# Пытаемся создать пользователя с email Алисы
		with pytest.raises(EmailAlreadyExistsError):
			user_repository.create("Тест3", "alice@example.com", 100)
		
		# Пытаемся создать пользователя с email Боба
		with pytest.raises(EmailAlreadyExistsError):
			user_repository.create("Тест4", "bob@example.com", 200)

	def test_get_by_id_existing(self, user_repository):
		"""Тест поиска существующего пользователя по ID."""
		user = user_repository.get_by_id(1)
		assert user is not None
		assert user.name == "Алиса"

	def test_get_by_id_not_found(self, user_repository):
		"""Тест поиска несуществующего пользователя по ID."""
		user = user_repository.get_by_id(999)
		assert user is None

	def test_get_by_email_existing(self, user_repository):
		"""Тест поиска существующего пользователя по email."""
		user = user_repository.get_by_email("alice@example.com")
		assert user is not None
		assert user.id == 1

	def test_get_by_email_not_found(self, user_repository):
		"""Тест поиска несуществующего пользователя по email."""
		user = user_repository.get_by_email("nonexistent@example.com")
		assert user is None

	def test_get_by_email_case_insensitive(self, user_repository):
		"""Тест поиска по email без учета регистра."""
		user = user_repository.get_by_email("ALICE@EXAMPLE.COM")
		assert user is not None
		assert user.id == 1

	def test_transfer_success(self, user_repository):
		"""Тест успешного перевода."""
		# Получаем начальные балансы
		alice = user_repository.get_by_id(1)
		bob = user_repository.get_by_id(2)
		initial_alice_balance = alice.balance
		initial_bob_balance = bob.balance
		
		# Выполняем перевод
		from_user, to_user = user_repository.transfer(1, 2, 50)
		
		# Проверяем что возвращенные объекты имеют правильные балансы
		assert from_user.balance == initial_alice_balance - 50
		assert to_user.balance == initial_bob_balance + 50
		
		# Проверяем что изменения сохранились в репозитории
		updated_alice = user_repository.get_by_id(1)
		updated_bob = user_repository.get_by_id(2)
		assert updated_alice.balance == initial_alice_balance - 50
		assert updated_bob.balance == initial_bob_balance + 50
		
		# Проверяем конкретные значения
		assert updated_alice.balance == 50  # было 100, стало 50
		assert updated_bob.balance == 300   # было 250, стало 300
		
		# Проверяем что общая сумма не изменилась
		total_before = initial_alice_balance + initial_bob_balance
		total_after = updated_alice.balance + updated_bob.balance
		assert total_before == total_after, "Общая сумма изменилась после перевода"

	def test_transfer_user_not_found(self, user_repository):
		"""Тест перевода с несуществующим пользователем."""
		with pytest.raises(UserNotFoundError):
			user_repository.transfer(999, 2, 50)
		
		with pytest.raises(UserNotFoundError):
			user_repository.transfer(1, 999, 50)

	def test_transfer_self_transfer(self, user_repository):
		"""Тест попытки перевода самому себе."""
		with pytest.raises(SelfTransferError):
			user_repository.transfer(1, 1, 50)

	def test_transfer_insufficient_funds(self, user_repository):
		"""Тест перевода при недостатке средств."""
		with pytest.raises(InsufficientFundsError):
			user_repository.transfer(1, 2, 1000)  # У Алисы только 100

	def test_transfer_invalid_amount_zero(self, user_repository):
		"""Тест перевода с нулевой суммой."""
		with pytest.raises(InvalidAmountError):
			user_repository.transfer(1, 2, 0)

	def test_transfer_invalid_amount_negative(self, user_repository):
		"""Тест перевода с отрицательной суммой."""
		with pytest.raises(InvalidAmountError):
			user_repository.transfer(1, 2, -10)

	def test_transfer_transaction_rollback(self, user_repository):
		"""Тест отката транзакции при ошибке."""
		# Получаем начальные балансы
		initial_alice = user_repository.get_by_id(1)
		initial_bob = user_repository.get_by_id(2)
		initial_alice_balance = initial_alice.balance
		initial_bob_balance = initial_bob.balance
		
		# Пытаемся выполнить перевод с ошибкой
		with pytest.raises(InsufficientFundsError):
			user_repository.transfer(1, 2, 1000)
		
		# Проверяем что балансы не изменились
		final_alice = user_repository.get_by_id(1)
		final_bob = user_repository.get_by_id(2)
		assert final_alice.balance == initial_alice_balance
		assert final_bob.balance == initial_bob_balance

	def test_transfer_transaction_success_values(self, user_repository):
		"""Тест корректности значений после успешного перевода."""
		# Получаем начальные балансы
		initial_alice = user_repository.get_by_id(1)
		initial_bob = user_repository.get_by_id(2)
		initial_alice_balance = initial_alice.balance
		initial_bob_balance = initial_bob.balance
		
		# Выполняем успешный перевод
		from_user, to_user = user_repository.transfer(1, 2, 50)
		
		# Проверяем что возвращенные объекты имеют правильные балансы
		assert from_user.balance == initial_alice_balance - 50
		assert to_user.balance == initial_bob_balance + 50
		
		# Проверяем что изменения сохранились в репозитории
		final_alice = user_repository.get_by_id(1)
		final_bob = user_repository.get_by_id(2)
		
		# Проверяем что у Алисы списалось 50
		assert final_alice.balance == initial_alice_balance - 50
		assert final_alice.balance == 50  # было 100, стало 50
		
		# Проверяем что Бобу начислилось 50
		assert final_bob.balance == initial_bob_balance + 50
		assert final_bob.balance == 300  # было 250, стало 300
		
		# Проверяем что общая сумма не изменилась
		total_before = initial_alice_balance + initial_bob_balance
		total_after = final_alice.balance + final_bob.balance
		assert total_before == total_after, "Общая сумма изменилась после перевода"


class TestEmptyUserRepository:
	"""Тесты для пустого репозитория пользователей."""

	def test_empty_repository_init(self, empty_user_repository):
		"""Тест инициализации пустого репозитория."""
		users = empty_user_repository.list()
		assert len(users) == 0

	def test_create_first_user(self, empty_user_repository):
		"""Тест создания первого пользователя в пустом репозитории."""
		user = empty_user_repository.create("Первый", "first@example.com", 100)
		assert user.id == 1
		assert len(empty_user_repository.list()) == 1

	def test_empty_repository_transfer_fails(self, empty_user_repository):
		"""Тест что перевод в пустом репозитории невозможен."""
		with pytest.raises(UserNotFoundError):
			empty_user_repository.transfer(1, 2, 50)
