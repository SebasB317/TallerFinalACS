class DomainException(Exception):
    """Excepción base del dominio"""
    pass

class InvalidEmailException(DomainException):
    """Email inválido"""
    pass

class InvalidPasswordException(DomainException):
    """Contraseña inválida"""
    pass

class UserAlreadyExistsException(DomainException):
    """Usuario ya existe"""
    pass

class UserNotFoundException(DomainException):
    """Usuario no encontrado"""
    pass

class InvalidCredentialsException(DomainException):
    """Credenciales inválidas"""
    pass

class TokenExpiredException(DomainException):
    """Token expirado"""
    pass

class InvalidTokenException(DomainException):
    """Token inválido"""
    pass

class PaymentValidationException(DomainException):
    """Error en validación de pago"""
    pass

class PaymentProcessingException(DomainException):
    """Error al procesar pago"""
    pass

class UnauthorizedException(DomainException):
    """No autorizado"""
    pass
