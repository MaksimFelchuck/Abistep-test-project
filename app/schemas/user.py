from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
	"""
	Схема для создания пользователя.
	
	Используется для валидации входящих данных при создании пользователя.
	"""
	
	name: str = Field(min_length=1, max_length=255)
	email: EmailStr
	balance: int | None = None  # если не передан — будет стартовое значение


class UserRead(BaseModel):
	"""
	Схема для чтения данных пользователя.
	
	Используется для возврата данных пользователя в API ответах.
	"""
	
	id: int
	name: str
	email: EmailStr
	balance: int
