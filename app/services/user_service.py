from pydantic import EmailStr

from app.core.config import settings
from app.repositories.user_repository import InMemoryUserRepository
from app.models.user import User


class UserService:
	"""
	Сервис для работы с пользователями.
	
	Предоставляет бизнес-логику для операций с пользователями,
	используя репозиторий для доступа к данным.
	"""
	
	def __init__(self, repo: InMemoryUserRepository) -> None:
		"""
		Инициализирует сервис с репозиторием пользователей.
		
		Args:
			repo: Репозиторий для работы с данными
		"""
		self.repo = repo

	def create_user(self, name: str, email: EmailStr, balance: int | None = None) -> User:
		"""
		Создает нового пользователя с валидацией данных.
		
		Args:
			name: Имя пользователя
			email: Email пользователя (валидируется Pydantic)
			balance: Начальный баланс (если не указан, берется из настроек)
			
		Returns:
			User: Созданный пользователь
			
		Raises:
			ValueError: Если email уже используется
		"""
		bal = settings.START_BALANCE if balance is None else balance
		return self.repo.create(name=name, email=str(email), balance=bal)

	def list_users(self) -> list:
		"""
		Возвращает список всех пользователей.
		
		Returns:
			list: Список пользователей
		"""
		return self.repo.list()

	def transfer(self, from_user_id: int, to_user_id: int, amount: int) -> tuple[User, User]:
		"""
		Переводит деньги между пользователями.
		
		Args:
			from_user_id: ID отправителя
			to_user_id: ID получателя
			amount: Сумма перевода
			
		Returns:
			tuple[User, User]: Кортеж (отправитель, получатель) с обновленными балансами
			
		Raises:
			ValueError: Если перевод невозможен
		"""
		return self.repo.transfer(from_user_id, to_user_id, amount)
