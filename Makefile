.PHONY: help install test lint format run build up down clean

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt

test: ## Запустить тесты локально
	pytest -v

test-cov: ## Запустить тесты с покрытием
	pytest --cov=app --cov-report=html

lint: ## Проверить код линтерами
	black --check app tests
	isort --check-only app tests
	flake8 app tests
	mypy app

format: ## Отформатировать код
	black app tests
	isort app tests

run: ## Запустить приложение локально
	uvicorn app.main:app --reload

# Docker команды
build: ## Собрать Docker образ
	docker-compose build

up: ## Запустить приложение в Docker
	docker-compose up --build

up-d: ## Запустить приложение в Docker (в фоне)
	docker-compose up --build -d

down: ## Остановить все сервисы
	docker-compose down

logs: ## Посмотреть логи
	docker-compose logs -f app

test-docker: ## Запустить тесты в Docker
	docker-compose run --rm test

clean: ## Очистить временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	docker-compose down --volumes --remove-orphans
