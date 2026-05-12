import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        v = (self.value or "").strip().lower()
        if not v or not _EMAIL_RE.match(v):
            raise ValueError("El email no tiene un formato válido.")
        object.__setattr__(self, "value", v)
