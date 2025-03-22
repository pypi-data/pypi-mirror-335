from typing import Any

from aiomexc.methods import MexcMethod
from aiomexc.types import MexcType


class MexcClientError(Exception):
    """
    Base exception for all mexc client errors.
    """


class DetailedMexcClientError(MexcClientError):
    """
    Base exception for all mexc client errors with a detailed message.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message})"


class MexcAPIError(DetailedMexcClientError):
    """
    Base exception for all mexc API errors.
    """

    label: str = "Mexc server says"

    def __init__(
        self,
        method: MexcMethod[MexcType],
        message: str,
    ) -> None:
        super().__init__(message=message)
        self.method = method

    def __str__(self) -> str:
        original_message = super().__str__()
        return f"{self.label} - {original_message}"


class MexcBadRequest(MexcAPIError):
    """
    Exception raised when request is malformed.
    """


class MexcNotFound(MexcAPIError):
    """
    Exception raised when order not found.
    """


class MexcApiKeyInvalid(MexcAPIError):
    """
    Exception raised when API key is invalid.
    """


class MexcApiKeyMissing(MexcAPIError):
    """
    Exception raised when API key is missing.
    """


class ClientDecodeError(MexcClientError):
    """
    Exception raised when client can't decode response. (Malformed response, etc.)
    """

    def __init__(self, message: str, original: Exception, data: Any) -> None:
        self.message = message
        self.original = original
        self.data = data

    def __str__(self) -> str:
        original_type = type(self.original)
        return (
            f"{self.message}\n"
            f"Caused from error: "
            f"{original_type.__module__}.{original_type.__name__}: {self.original}\n"
            f"Content: {self.data}"
        )
