from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextWorkCommand:
    """Comando encolado por el productor (API) y consumido por un worker."""

    job_id: int
    text_id: int
    user_id: int
    content: str
