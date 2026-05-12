from typing import Protocol


class JobRepository(Protocol):
    """Persistencia de trabajos y textos asociados."""

    def create_job_with_texts(self, user_id: int, texts: list[str]) -> tuple[int, list[int]]:
        """Crea job + filas de texto; devuelve (job_id, ids de textos en el mismo orden que `texts`)."""

    def mark_job_processing_if_pending(self, job_id: int) -> None: ...

    def mark_text_processing(self, text_id: int) -> int | None:
        """Pasa el texto a processing si estaba pending; devuelve job_id o None si no aplica."""

    def complete_text_with_result(self, text_id: int, sentiment: str, score: float) -> bool:
        """Solo si el texto estaba en `processing`. Actualiza resultado y avanza contador del job."""

    def mark_text_failed(self, text_id: int) -> bool:
        """Marca failed un texto pending o processing; avanza contador del job."""
