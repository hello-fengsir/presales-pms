from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "售前CRM系统"
    secret_key: str = "crm-secret-change-in-production"
    admin_username: str = "admin"
    admin_password: str = "admin123"
    access_token_expire_minutes: int = 60 * 24 * 7

    class Config:
        env_file = ".env"

settings = Settings()
