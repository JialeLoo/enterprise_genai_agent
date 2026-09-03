class ExternalServiceError(Exception):
    pass


class ExternalServiceTimeout(
    ExternalServiceError
):
    pass


class ExternalServiceUnavailable(
    ExternalServiceError
):
    pass


class ResourceNotFoundError(
    ExternalServiceError
):
    pass