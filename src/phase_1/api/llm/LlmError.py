class LlmError(Exception):
    """
    Raised when a provider cannot produce an answer, so the HTTP layer can react to a provider failure
    without knowing which provider is behind it.
    `statusCode` is the HTTP status the API should answer with, keeping that decision out of the router.
    """
    def __init__(self, message: str, statusCode: int = 502) -> None:
        super().__init__(message)
        self.statusCode = statusCode
