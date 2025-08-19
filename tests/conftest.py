"""
Конфигурация pytest и общие фикстуры.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.user_repository import InMemoryUserRepository
from app.services.user_service import UserService


@pytest.fixture(scope="session")
def app_instance():
	"""
	Фикстура для экземпляра приложения (сессионная область).
	"""
	return app


@pytest.fixture
def client(app_instance):
	"""
	Фикстура для тестового клиента FastAPI.
	"""
	return TestClient(app_instance)


@pytest.fixture
def user_repository():
	"""
	Фикстура для репозитория пользователей.
	Содержит тестовых пользователей (Алиса и Боб).
	"""
	return InMemoryUserRepository()


@pytest.fixture
def user_service(user_repository):
	"""
	Фикстура для сервиса пользователей.
	"""
	return UserService(user_repository)


@pytest.fixture
def empty_user_repository():
	"""
	Фикстура для пустого репозитория пользователей.
	Используется для тестов, где нужен чистый репозиторий.
	"""
	repo = InMemoryUserRepository()
	# Очищаем тестовых пользователей
	repo._users.clear()
	repo._next_id = 1
	return repo


@pytest.fixture
def empty_user_service(empty_user_repository):
	"""
	Фикстура для сервиса с пустым репозиторием.
	"""
	return UserService(empty_user_repository)
