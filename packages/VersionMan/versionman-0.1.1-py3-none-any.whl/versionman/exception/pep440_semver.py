from versionman.exception.base import VersionManException as _VersionManException


class VersionManPEP440SemVerException(_VersionManException):
    """Base exception for all PEP440SemVer exceptions."""

    def __init__(self, message: str):
        super().__init__(message)
        return


class VersionManInvalidPEP440SemVerError(VersionManPEP440SemVerException):
    """Exception raised when an invalid input is provided to PEP440SemVer."""

    def __init__(self, version: str, description: str = ""):
        message = f"Input version '{version}' is invalid. {description}".strip()
        super().__init__(message)
        return