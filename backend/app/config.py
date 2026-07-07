from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centralized app configuration. Values are read from environment variables
    (or a local .env file) — never hardcode secrets directly in code.
    """

    # General
    APP_NAME: str = "AI Resume Improvement Platform API"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./resume_platform.db"

    # JWT auth
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # CORS — the frontend origin(s) allowed to call this API.
    # Comma-separated so you can allow more than one (e.g. localhost + 127.0.0.1,
    # or if Vite falls back to a different port because 5173 was already taken).
    FRONTEND_ORIGIN: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174"
    )

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGIN.split(",") if origin.strip()]

    # Gemini (used starting Milestone 10)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"  # stable, free-tier model as of mid-2026

    # File uploads
    UPLOAD_DIR: str = "uploaded_resumes"
    MAX_UPLOAD_SIZE_MB: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
