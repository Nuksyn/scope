from dataclasses import FrozenInstanceError
from ipaddress import ip_address

import pytest

from domainscope.exceptions import InvalidTargetError, InvalidDomainError
from domainscope.helpers.target import Target, DomainTarget, IPTarget


@pytest.mark.parametrize("raw, expected", [
    ("example.com", "example.com"),
    ("www.example.com", "www.example.com"),  # www is never stripped
    ("  Example.COM  ", "example.com"),  # spaces and case
    ("example.com.", "example.com"),  # trailing dot (DNS form)
    (".example.com", "example.com"),  # leading dot (cookie/nginx form)
    ("https://example.com/shop?x=1", "example.com"),  # scheme, path, query
    ("example.com:8080", "example.com"),  # port, no scheme
    ("https://example.com./shop", "example.com"),  # trailing dot inside a URL
    ("_dmarc.example.com", "_dmarc.example.com"),  # underscore names stay ASCII
    ("bücher.de", "xn--bcher-kva.de"),  # IDN to punycode
    ("https://Bücher.de/shop", "xn--bcher-kva.de"),  # IDN inside a URL
    ("com", "com"),  # single label is allowed
])
def test_parse_domain(raw, expected):
    assert Target.parse(raw) == DomainTarget(expected)


@pytest.mark.parametrize("raw, expected", [
    ("1.1.1.1", "1.1.1.1"),
    (" 1.1.1.1 ", "1.1.1.1"),
    ("1.1.1.1.", "1.1.1.1"),
    ("1.1.1.1:80", "1.1.1.1"),
    ("http://1.1.1.1/x", "1.1.1.1"),
    ("2606:4700:4700::1111", "2606:4700:4700::1111"),  # bare IPv6
    ("2606:4700:4700:0:0:0:0:1111", "2606:4700:4700::1111"),  # long form
    ("https://[2606:4700:4700::1111]:443/", "2606:4700:4700::1111"),
])
def test_parse_ip(raw, expected):
    assert Target.parse(raw) == IPTarget(ip_address(expected))


@pytest.mark.parametrize("raw", [
    "1.1.1.0/24",
    "1.1.1.1/24",  # host bits set
    "2606:4700::/32",  # IPv6 range
    "ex@mple.com",  # character with @
    "https://",  # no host
    "",   # empty input
])
def test_parse_rejects_bad_target(raw):
    with pytest.raises(InvalidTargetError):
        Target.parse(raw)


@pytest.mark.parametrize("raw", [
    "exa..mple.com",  # empty label
    "-example.com",  # label starts with a dash
    "example-.com",  # label ends with a dash
    "ex!mple.com",  # character outside ALLOWED
    "1.1.1.1333",  # all-digit TLD
    "a" * 64 + ".com",  # label over 63 characters
    "a." * 127 + "com",  # whole name over 253 characters
    "bü_cher.de",  # rejected by idna
])
def test_parse_rejects_bad_domain(raw):
    with pytest.raises(InvalidDomainError):
        Target.parse(raw)


def test_host_property():
    assert Target.parse("example.com").host == "example.com"
    assert Target.parse("1.1.1.1").host == "1.1.1.1"


def test_target_is_abstract():
    with pytest.raises(TypeError):
        Target()


def test_target_is_frozen():
    target = Target.parse("example.com")
    with pytest.raises(FrozenInstanceError):
        target.name = "other.com"
