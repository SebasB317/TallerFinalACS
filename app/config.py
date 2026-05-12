from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-secret-change-in-production-min-32-chars!!"
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    database_url: str = "sqlite:///./taller_final.db"
    worker_count: int = 4
    max_texts_per_job: int = 100
    # Simulación CPU-bound (~50 ms por texto, criterio del enunciado)
    analysis_sleep_min_sec: float = 0.045
    analysis_sleep_max_sec: float = 0.055
    # Probabilidad de timeout simulado por texto (0 en tests; p.ej. 0.03 en demo)
    simulated_analysis_timeout_probability: float = 0.0


settings = Settings()
