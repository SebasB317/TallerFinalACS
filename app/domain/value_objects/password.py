import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlainPassword:
    """Contraseña en claro solo para validación y hashing; no persistir."""

    value: str

    def __post_init__(self) -> None:
        p = self.value or ""
        if len(p) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", p):
            raise ValueError("La contraseña debe incluir al menos una mayúscula.")
        if not re.search(r"\d", p):
            raise ValueError("La contraseña debe incluir al menos un número.")
