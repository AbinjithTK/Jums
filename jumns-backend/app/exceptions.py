"""Custom exception classes for the Jumns API."""


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource"):
        self.resource = resource
        super().__init__(f"{resource} not found")


class AgentUnavailableError(Exception):
    """Raised when all AI models fail."""

    pass


class RateLimitExceededError(Exception):
    """Raised when free-tier daily message limit is reached."""

    def __init__(self, limit: int = 10):
        self.limit = limit
        super().__init__(f"Daily message limit ({limit}) reached")


class UnauthorizedError(Exception):
    """Raised when JWT validation fails."""

    pass
