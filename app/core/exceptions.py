"""
Кастомные исключения для бизнес-логики.
"""


class UserNotFoundError(Exception):
	"""Пользователь не найден."""
	pass


class SelfTransferError(Exception):
	"""Попытка перевода самому себе."""
	pass


class InsufficientFundsError(Exception):
	"""Недостаточно средств для перевода."""
	pass


class InvalidAmountError(Exception):
	"""Некорректная сумма перевода."""
	pass


class EmailAlreadyExistsError(Exception):
	"""Email уже используется."""
	pass
