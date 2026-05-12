class DomainError(Exception):
    """Error de reglas de negocio en el dominio."""


class EmailAlreadyRegisteredError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class UserNotFoundError(DomainError):
    pass


class TooManyTextsInBatchError(DomainError):
    """El lote supera el máximo permitido (100 textos)."""


class EmptyJobBatchError(DomainError):
    """No se puede crear un trabajo sin textos."""


class JobNotFoundError(DomainError):
    """Trabajo inexistente o sin permiso para verlo."""


class JobNotReadyForReportError(DomainError):
    """El reporte agregado solo aplica cuando el trabajo está `completed`."""
