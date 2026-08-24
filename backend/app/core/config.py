from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Complaint thresholds (days)
    OVERDUE_THRESHOLD_DAYS: int = 7
    LOW_TO_MEDIUM_DAYS: int = 3
    MEDIUM_TO_HIGH_DAYS: int = 5

    # ImageKit
    IMAGEKIT_PUBLIC_KEY: str = ""
    IMAGEKIT_PRIVATE_KEY: str = ""
    IMAGEKIT_URL_ENDPOINT: str = ""

    # Email
    EMAIL_API_KEY: str = ""
    EMAIL_FROM: str = ""
    GMAIL_EMAIL: str = ""
    GMAIL_APP_PASSWORD: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()  # type: ignore[call-arg]
