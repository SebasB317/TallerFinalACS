import re
from app.domain.exceptions import InvalidEmailException

class Email:
    """Value Object para Email"""
    
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise InvalidEmailException(f"Email inválido: {value}")
        self.value = value.lower()
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
