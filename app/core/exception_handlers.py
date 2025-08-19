"""
Exception handlers для FastAPI.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import (
	UserNotFoundError, SelfTransferError, 
	InsufficientFundsError, InvalidAmountError, EmailAlreadyExistsError
)


async def user_not_found_handler(request: Request, exc: UserNotFoundError):
	"""Обработчик для UserNotFoundError."""
	return JSONResponse(
		status_code=404,
		content={"detail": "Пользователь не найден"}
	)


async def self_transfer_handler(request: Request, exc: SelfTransferError):
	"""Обработчик для SelfTransferError."""
	return JSONResponse(
		status_code=400,
		content={"detail": "Нельзя переводить деньги самому себе"}
	)


async def insufficient_funds_handler(request: Request, exc: InsufficientFundsError):
	"""Обработчик для InsufficientFundsError."""
	return JSONResponse(
		status_code=400,
		content={"detail": "Недостаточно средств для перевода"}
	)


async def invalid_amount_handler(request: Request, exc: InvalidAmountError):
	"""Обработчик для InvalidAmountError."""
	return JSONResponse(
		status_code=400,
		content={"detail": "Некорректная сумма перевода"}
	)


async def email_already_exists_handler(request: Request, exc: EmailAlreadyExistsError):
	"""Обработчик для EmailAlreadyExistsError."""
	return JSONResponse(
		status_code=409,
		content={"detail": "Email уже используется"}
	)
