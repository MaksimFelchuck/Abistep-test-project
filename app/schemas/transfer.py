from pydantic import BaseModel, Field


class TransferCreate(BaseModel):
	"""
	Схема для создания перевода денег.
	
	Используется для валидации входящих данных при переводе.
	"""
	
	from_user_id: int = Field(gt=0, description="ID отправителя")
	to_user_id: int = Field(gt=0, description="ID получателя")
	amount: int = Field(gt=0, description="Сумма перевода")


class TransferResponse(BaseModel):
	"""
	Схема для ответа на операцию перевода.
	
	Используется для возврата информации о результате перевода.
	"""
	
	from_user_id: int
	to_user_id: int
	amount: int
	from_user_balance: int
	to_user_balance: int
	message: str = "Перевод выполнен успешно"
