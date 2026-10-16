from abc import ABC, abstractmethod
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network
from urllib.parse import urlsplit
import string

import idna

from domainscope.exceptions import InvalidTargetError, InvalidDomainError

ALLOWED = set(string.ascii_lowercase + string.digits + "-_")

class Target(ABC):
    """A parsed domain or IP; create one with Target.parse()."""

    @property
    @abstractmethod
    def host(self) -> str:
        """The string checks connect to (domain name or IP)."""

    @staticmethod
    def _clean(raw: str) -> str:
        """removes spaces and fixes uppercases in lower-ones"""
        return raw.strip().lower()

    @staticmethod
    def _reject_cidr(cleaned: str) -> None:
        """Raise InvalidTargetError if the input is a bare CIDR range."""
        try:
            ip_network(cleaned, strict=False)
        except ValueError:
            return

        if "/" not in cleaned:
            return
        raise InvalidTargetError(f"{cleaned!r} is a CIDR range; give a single IP or domain")

    @staticmethod
    def _as_ip(cleaned: str) -> IPv4Address | IPv6Address | None:
        """Return the input as an IP object, or None if it isn't one."""
        try:
            return ip_address(cleaned)
        except ValueError:
            return None

    @staticmethod
    def _extract_host(cleaned: str) -> str:
        """Return the bare host from a URL-ish input; raise if there is none."""
        url = "//" + cleaned if "://" not in cleaned else cleaned
        hostname = urlsplit(url).hostname
        if hostname is None:
            raise InvalidTargetError(f"{cleaned!r} has no host")
        return hostname.strip(".")

    @staticmethod
    def _to_punycode(host: str) -> str:
        """Convert a non-ASCII domain to punycode; ASCII names pass through."""
        if host.isascii():
            return host
        try:
            return idna.encode(host).decode("ascii")
        except idna.IDNAError as e:
            raise InvalidDomainError(f"{host!r} is not a valid "
                                     "domain name") from e

    @staticmethod
    def _validate_domain(host: str) -> None:
        """Raise InvalidDomainError if host breaks DNS naming rules."""
        if len(host) > 253:
            raise InvalidDomainError(f"{host!r} is too long")
        labels = host.split(".")
        for label in labels:
            if not 1 <= len(label) <= 63:
                raise InvalidDomainError(f"{host!r} is too long or too short (empty)")
            if label.startswith("-") or label.endswith("-"):
                raise InvalidDomainError(f"{host!r} label starts or ends with dash.")
            if not all(ch in ALLOWED for ch in label):
                raise InvalidDomainError(f"{host!r} is not a valid domain name")
        if labels[-1].isdigit():
            raise InvalidDomainError(f"{host!r}: the TLD can't be all digits")

    @classmethod
    def parse(cls, raw: str) -> "DomainTarget | IPTarget":
        """Turn raw user input into an IPTarget or DomainTarget."""
        cleaned = cls._clean(raw)
        cls._reject_cidr(cleaned)

        host = cleaned if cls._as_ip(cleaned) is not None \
            else cls._extract_host(cleaned)
        ip = cls._as_ip(host)
        if ip is not None:
            return IPTarget(ip)
        final_domain = cls._to_punycode(host)
        cls._validate_domain(final_domain)
        return DomainTarget(final_domain)


@dataclass(frozen=True)
class DomainTarget(Target):
    name: str

    @property
    def host(self) -> str:
        return self.name


@dataclass(frozen=True)
class IPTarget(Target):
    ip: IPv4Address | IPv6Address

    @property
    def host(self) -> str:
        return str(self.ip)  # IP object str returns the raw IP address


