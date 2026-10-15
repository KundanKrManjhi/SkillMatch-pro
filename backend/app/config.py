from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://127.0.0.1:27017"
    database_name: str = "smart_skill_job"
    jwt_secret_key: str = "dev-only-change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    frontend_origin: str = "http://localhost:5173"
    admin_name: str = "Platform Admin"
    admin_email: str = "admin@skillmatch.com"
    admin_password: str = "ChangeMe12345!"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

settings = Settings()
