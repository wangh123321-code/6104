from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/youth_training"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    PROMOTION_WEIGHT_TECHNIQUE: float = 0.30
    PROMOTION_WEIGHT_FITNESS: float = 0.20
    PROMOTION_WEIGHT_MATCH: float = 0.25
    PROMOTION_WEIGHT_PHYSICAL: float = 0.25

    PROMOTION_AUTO_SUGGEST_THRESHOLD: float = 0.25

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
