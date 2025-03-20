class RevoizeError(Exception):
    pass


class RequestError(RevoizeError):
    pass


class InvalidResponseSchema(RevoizeError):
    pass


class EnhancementTimeoutError(RevoizeError, TimeoutError):
    pass
