from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""
	Настройки приложения.
	
	Загружает конфигурацию из переменных окружения и .env файла.
	Предоставляет значения по умолчанию для основных параметров.
	"""
	
	PROJECT_NAME: str = "Abistep Test Project"
	VERSION: str = "0.1.0"
	API_V1_PREFIX: str = "/api/v1"
	START_BALANCE: int = 0

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)


settings = Settings()
