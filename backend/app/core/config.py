from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    # Fora do Docker (Alembic, pytest, uvicorn no venv): 127.0.0.1:5433,
    # a porta que o Compose publica no host.
    # Dentro do Compose, a API sobrescreve com db:5432 (nome do serviço).
    db_host: str = "127.0.0.1"
    db_port: int = 5433
    # Local (Docker): prefer. Produção (Neon): require, conexão só com SSL
    db_sslmode: str = "prefer"

    @property
    def database_url(self) -> str:
        # URL.create escapa caracteres especiais da senha (@, :, /...)
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.db_host,
            port=self.db_port,
            database=self.postgres_db,
            query={"sslmode": self.db_sslmode},
        ).render_as_string(hide_password=False)


settings = Settings()
