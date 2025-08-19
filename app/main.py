from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.api.v1.router import router as api_v1_router
from app.core.exception_handlers import (
	user_not_found_handler, self_transfer_handler, insufficient_funds_handler,
	invalid_amount_handler, email_already_exists_handler
)
from app.core.exceptions import (
	UserNotFoundError, SelfTransferError, InsufficientFundsError,
	InvalidAmountError, EmailAlreadyExistsError
)


app = FastAPI(
	title=settings.PROJECT_NAME,
	version=settings.VERSION,
	default_response_class=ORJSONResponse,
)


@app.get("/", tags=["meta"])
def read_root() -> dict:
	"""
	Корневой эндпоинт для получения мета-информации о проекте.
	
	Returns:
		dict: Словарь с названием проекта и версией
	"""
	return {"name": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/health", tags=["infra"])
def health() -> dict:
	"""
	Эндпоинт для проверки состояния приложения (healthcheck).
	
	Returns:
		dict: Словарь со статусом "ok"
	"""
	return {"status": "ok"}


# Регистрируем exception handlers
app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(SelfTransferError, self_transfer_handler)
app.add_exception_handler(InsufficientFundsError, insufficient_funds_handler)
app.add_exception_handler(InvalidAmountError, invalid_amount_handler)
app.add_exception_handler(EmailAlreadyExistsError, email_already_exists_handler)


app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
