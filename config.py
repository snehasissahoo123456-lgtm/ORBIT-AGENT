from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    orbit_name: str = "ORBIT"
    orbit_host: str = "127.0.0.1"
    orbit_port: int = 8000
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:7b"
    orbit_workspace: str = "./workspace"
    orbit_database: str = "./data/orbit.sqlite3"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def workspace(self) -> Path:
        path = Path(self.orbit_workspace).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def database(self) -> Path:
        path = Path(self.orbit_database).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
