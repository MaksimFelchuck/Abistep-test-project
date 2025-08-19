from dataclasses import dataclass


@dataclass
class User:
	"""
	Модель пользователя.
	
	Представляет пользователя в системе с основными атрибутами:
	- id: уникальный идентификатор
	- name: имя пользователя
	- email: электронная почта
	- balance: текущий баланс
	"""
	
	id: int
	name: str
	email: str
	balance: int
