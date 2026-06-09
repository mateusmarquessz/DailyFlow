class ServiceError(Exception):
    """Base class for service-layer errors translated to HTTP responses by controllers."""


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class UnauthorizedError(ServiceError):
    pass


class ValidationError(ServiceError):
    pass
