from fastapi import Depends

from app.repositories.user_repository import InMemoryUserRepository
from app.services.user_service import UserService

# Создаем один экземпляр репозитория для всего приложения
_user_repository = InMemoryUserRepository()


def get_user_repository() -> InMemoryUserRepository:
	"""
	Dependency для получения репозитория пользователей.
	
	Returns:
		InMemoryUserRepository: Экземпляр репозитория
	"""
	return _user_repository


def get_user_service(repo: InMemoryUserRepository = Depends(get_user_repository)) -> UserService:
	"""
	Dependency для получения сервиса пользователей.
	
	Args:
		repo: Репозиторий пользователей
		
	Returns:
		UserService: Экземпляр сервиса
	"""
	return UserService(repo)
