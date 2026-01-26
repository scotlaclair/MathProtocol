"""
Custom exception classes for MathProtocol.

These exceptions provide structured error handling for various
protocol operations including registry management, firewall operations,
and validation failures.
"""


class MathProtocolError(Exception):
    """Base exception for MathProtocol errors."""
    pass


class RegistryError(MathProtocolError):
    """Raised when registry operations fail."""
    pass


class FirewallError(MathProtocolError):
    """Raised when firewall operations fail."""
    pass


class ValidationError(MathProtocolError):
    """Raised when validation fails."""
    pass
