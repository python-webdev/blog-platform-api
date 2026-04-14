class NotFoundError(Exception):
    def __init__(self, resource: str, identifier: str | int) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(
            f"{resource} with identifier '{identifier}' not found"
        )


class PermissionDeniedError(Exception):
    def __init__(self, action: str) -> None:
        self.action = action
        super().__init__(f"Permission denied: {action}")


class ConflictError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class BusinessRuleViolationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
