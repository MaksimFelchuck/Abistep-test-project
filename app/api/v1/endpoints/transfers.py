from fastapi import APIRouter, Depends

from app.schemas.transfer import TransferCreate, TransferResponse
from app.services.user_service import UserService
from app.dependencies.user_dependencies import get_user_service


router = APIRouter()


@router.post("", response_model=TransferResponse, status_code=200, summary="Перевести деньги")
def transfer_money(
	payload: TransferCreate,
	service: UserService = Depends(get_user_service)
) -> TransferResponse:
	"""
	Переводит деньги между пользователями.
	
	Args:
		payload: Данные для перевода
		service: Сервис пользователей
		
	Returns:
		TransferResponse: Результат операции перевода
	"""
	from_user, to_user = service.transfer(
		from_user_id=payload.from_user_id,
		to_user_id=payload.to_user_id,
		amount=payload.amount
	)
	
	return TransferResponse(
		from_user_id=from_user.id,
		to_user_id=to_user.id,
		amount=payload.amount,
		from_user_balance=from_user.balance,
		to_user_balance=to_user.balance,
	)
