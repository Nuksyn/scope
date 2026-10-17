from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """How bad a finding is."""
    INFO = 0
    WARNING = 1
    CRITICAL = 2

@dataclass(frozen=True)
class Finding:
    """One issue a check found: how bad, a short code and a plain-language message."""
    severity: Severity
    code: str
    message: str


    def __post_init__(self):
        if not isinstance(self.severity, Severity):
            raise TypeError(f"severity must be a Severity, got {type(self.severity).__name__}")
        return


