from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Cinema Commander"
    app_env: str = "development"
    google_cloud_project: str = ""
    google_cloud_location: str = "global"
    google_genai_use_vertexai: str = "TRUE"
    gemini_model: str = "gemini-3.5-flash"
    parallel_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
