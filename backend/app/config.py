from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://*.up.railway.app"
    CACHE_TTL: int = 30
    REFRESH_INTERVAL: int = 45

    class Config:
        env_prefix = "SIBT_"


settings = Settings()
