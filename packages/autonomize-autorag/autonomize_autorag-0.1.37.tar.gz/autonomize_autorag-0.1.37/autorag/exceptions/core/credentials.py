"""Exceptions for the modelhub credentials module."""


class ModelhubCredentialException(Exception):
    """Base exception for ModelhubCredential exceptions."""


class ModelhubMissingCredentialsException(ModelhubCredentialException):
    """Raised when modelhub credentials are provided."""


class ModelhubInvalidTokenException(ModelhubCredentialException):
    """Raised when an ill-formatted or invalid token is provided."""


class ModelhubTokenRetrievalException(ModelhubCredentialException):
    """Raised when the token could not be retrieved."""


class ModelhubUnauthorizedException(ModelhubCredentialException):
    """Raised when the modelhub credentials are invalid."""
