class VersionManException(Exception):
    """Base exception for all versionman exceptions."""

    def __init__(self, message: str):
        super().__init__(message)
        return