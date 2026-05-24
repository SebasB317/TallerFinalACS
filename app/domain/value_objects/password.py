import re
from app.domain.exceptions import InvalidPasswordException

class Password:
    """Value Object para Contraseña"""
    
    MIN_LENGTH = 8
    
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise InvalidPasswordException(
                f"Contraseña debe tener al menos {self.MIN_LENGTH} caracteres, "
                "una mayúscula y un número"
            )
        self.value = value
    
    @staticmethod
    def _is_valid(password: str) -> bool:
        if len(password) < Password.MIN_LENGTH:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Password):
            return self.value == other.value
        return False
