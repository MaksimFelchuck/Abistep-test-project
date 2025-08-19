from app.models.user import User
from app.core.exceptions import (
	UserNotFoundError, SelfTransferError, 
	InsufficientFundsError, InvalidAmountError, EmailAlreadyExistsError
)


class InMemoryUserRepository:
	"""
	In-memory репозиторий для работы с пользователями.
	
	Имитирует базу данных, храня данные в памяти приложения.
	Содержит тестовых пользователей и поддерживает базовые CRUD операции.
	"""
	
	def __init__(self) -> None:
		"""
		Инициализирует репозиторий с тестовыми данными.
		"""
		# Имитируем базу данных с тестовыми данными
		self._users: list = [
			User(id=1, name="Алиса", email="alice@example.com", balance=100),
			User(id=2, name="Боб", email="bob@example.com", balance=250),
		]
		self._next_id: int = 3

	def _create_snapshot(self) -> dict:
		"""
		Создает снимок текущего состояния пользователей.
		
		Returns:
			dict: Словарь с копиями пользователей
		"""
		return {user.id: User(
			id=user.id,
			name=user.name,
			email=user.email,
			balance=user.balance
		) for user in self._users}

	def _restore_snapshot(self, snapshot: dict) -> None:
		"""
		Восстанавливает состояние из снимка.
		
		Args:
			snapshot: Снимок состояния для восстановления
		"""
		for user in self._users:
			if user.id in snapshot:
				user.name = snapshot[user.id].name
				user.email = snapshot[user.id].email
				user.balance = snapshot[user.id].balance

	def list(self) -> list:
		"""
		Возвращает список всех пользователей.
		
		Returns:
			list: Копия списка пользователей
		"""
		return self._users.copy()

	def get_by_id(self, user_id: int) -> User | None:
		"""
		Находит пользователя по ID.
		
		Args:
			user_id: ID пользователя для поиска
			
		Returns:
			User | None: Найденный пользователь или None
		"""
		for user in self._users:
			if user.id == user_id:
				return user
		return None

	def get_by_email(self, email: str) -> User | None:
		"""
		Находит пользователя по email (регистронезависимо).
		
		Args:
			email: Email пользователя для поиска
			
		Returns:
			User | None: Найденный пользователь или None
		"""
		for user in self._users:
			if user.email.lower() == email.lower():
				return user
		return None

	def create(self, name: str, email: str, balance: int) -> User:
		"""
		Создает нового пользователя.
		
		Args:
			name: Имя пользователя
			email: Email пользователя (должен быть уникальным)
			balance: Начальный баланс пользователя
			
		Returns:
			User: Созданный пользователь
			
		Raises:
			EmailAlreadyExistsError: Если email уже используется
		"""
		# Проверяем уникальность email
		if self.get_by_email(email):
			raise EmailAlreadyExistsError()

		user = User(
			id=self._next_id,
			name=name,
			email=email,
			balance=balance,
		)
		self._users.append(user)
		self._next_id += 1
		return user

	def transfer(self, from_user_id: int, to_user_id: int, amount: int) -> tuple[User, User]:
		"""
		Переводит деньги между пользователями с поддержкой транзакций.
		
		Args:
			from_user_id: ID отправителя
			to_user_id: ID получателя
			amount: Сумма перевода
			
		Returns:
			tuple[User, User]: Кортеж (отправитель, получатель) с обновленными балансами
			
		Raises:
			UserNotFoundError: Если пользователь не найден
			SelfTransferError: Если попытка перевода самому себе
			InsufficientFundsError: Если недостаточно средств
			InvalidAmountError: Если некорректная сумма
		"""
		# Создаем снимок состояния перед изменениями
		snapshot = self._create_snapshot()

		# Аналог атамарной транзакции
		# если алиса переводит Бобу 10р, с её счёта сняли 10 р, а бобу на счёт +10р,
		# но, если при пополнении счёта Бобу возникнет ошибка, то Алисе нужно вернуть 10р
		try:
			# Проверяем что пользователи существуют
			from_user = self.get_by_id(from_user_id)
			if not from_user:
				raise UserNotFoundError()
				
			to_user = self.get_by_id(to_user_id)
			if not to_user:
				raise UserNotFoundError()
			
			# Проверяем что не переводим самому себе
			if from_user_id == to_user_id:
				raise SelfTransferError()
			
			# Проверяем что у отправителя хватает денег
			if from_user.balance < amount:
				raise InsufficientFundsError()
			
			# Проверяем что сумма положительная
			if amount <= 0:
				raise InvalidAmountError()
			
			# Выполняем перевод
			from_user.balance -= amount
			to_user.balance += amount
			
			return from_user, to_user
			
		except Exception:
			# При любой ошибке откатываем изменения
			self._restore_snapshot(snapshot)
			raise
