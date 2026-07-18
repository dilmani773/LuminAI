from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://luminai:luminai@localhost:5432/luminai"

    # Auth
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # LLM
    llm_provider: str = "gemini"  # or "claude"
    gemini_api_key: str = ""
    anthropic_api_key: str = ""

    # File storage (local disk for the hackathon build - swap for S3/cloud storage before real deployment)
    upload_dir: str = "/app/uploaded_files"

    class Config:
        env_file = ".env"


settings = Settings()