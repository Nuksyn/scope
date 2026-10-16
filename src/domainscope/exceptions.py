class DomainScopeError(Exception):
    """General error for DomainScope"""


class InvalidTargetError(DomainScopeError):
    """Incorrect target"""


class InvalidDomainError(InvalidTargetError):
    """Invalid domain"""
