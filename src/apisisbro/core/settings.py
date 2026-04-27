from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    DATABASE_URL: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    # configuracao de negocio
    DESCONTO_ATACADO_PERCENTUAL: int = 37
    ALERTA_VALIDADE_DIAS: int = 30
    ALERTA_ESTOQUE_MINIMO: int = 10

    # Storage

    STORAGE_BUCKET_PRODUTOS: str
    STORAGE_BUCKET_COMPROVANTES: str
    MAX_UPLOAD_SIZE_MB: int = 8

    @property
    def max_upload_size_bytes(self) -> int:
        """Retorna tamanho máximo de upload em bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Verifica se está em produção."""
        return self.APP_ENV == 'production'


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()


settings = get_settings()
