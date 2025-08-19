from fastapi import APIRouter, Depends

from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService
from app.dependencies.user_dependencies import get_user_service


router = APIRouter()


@router.post("", response_model=UserRead, status_code=201, summary="Создать пользователя")
def create_user(
	payload: UserCreate, 
	service: UserService = Depends(get_user_service)
) -> UserRead:
	"""
	Создает нового пользователя в системе.
	
	Args:
		payload: Данные для создания пользователя
		service: Сервис пользователей
		
	Returns:
		UserRead: Созданный пользователь
	"""
	user = service.create_user(name=payload.name, email=payload.email, balance=payload.balance)
	return UserRead.model_validate(user.__dict__)


@router.get("", response_model=list[UserRead], summary="Список пользователей")
def list_users(service: UserService = Depends(get_user_service)) -> list[UserRead]:
	"""
	Возвращает список всех пользователей в системе.
	
	Args:
		service: Сервис пользователей
		
	Returns:
		list[UserRead]: Список пользователей
	"""
	return [UserRead.model_validate(u.__dict__) for u in service.list_users()]
