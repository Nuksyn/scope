import pytest

from domainscope.helpers.findings import Severity, Finding
from domainscope.helpers.printer import Printer, Status, HEADER_LEAD


def section_lines_helper(capsys, *args):
    """Prints one section with one line(*args) and returns the output lines."""
    printer = Printer()
    with printer.section("SSL Certificate"):
        printer.line(*args)
    out = capsys.readouterr().out
    return out.splitlines()


def test_target_line(capsys):
    Printer().target("example.com")
    out = capsys.readouterr().out
    assert out == "[*] Target :: example.com\n"


def test_from_bool():
    check_one = Status.from_bool(True)
    check_two = Status.from_bool(False)
    assert check_one is Status.OK
    assert check_two is Status.FAIL

def test_section(capsys):
    result = section_lines_helper(capsys, "Issuer", "R11", Status.OK)
    assert result[0].startswith(HEADER_LEAD + "SSL Certificate")
    assert result[1] == "[+] Issuer :: R11"
    assert set(result[2]) == {"═"}
    assert result[3] == ""


def test_line_without_status(capsys):
    result = section_lines_helper(capsys, "Server", "nginx")
    assert result[1] == " Server :: nginx"


def test_markup_is_not_parsed(capsys):
    result = section_lines_helper(capsys, "TXT", "[red]hi[/]")
    assert result[1] == " TXT :: [red]hi[/]"


@pytest.mark.parametrize("severity, expected", [
    (Severity.CRITICAL, Status.FAIL),
    (Severity.INFO, Status.INFO),
    (Severity.WARNING, Status.WARN),
])
def test_severity_matching_status(severity, expected):
    assert Status.from_severity(severity) is expected


@pytest.mark.parametrize("severity", [
    None,
    "AI is coming after our jobs",
    "kekw",
    2,
    "CRITICAL",
])
def test_severity_invalid_input(severity):
    with pytest.raises(KeyError):
        Status.from_severity(severity)


@pytest.mark.parametrize("severity",
    list(Severity)
)
def test_that_every_severity_is_mapped(severity):
    assert isinstance(Status.from_severity(severity), Status)


# @pytest.mark.parametrize("severity", [])

def test_finding_order_and_values(capsys):
    printer = Printer()
    f = Finding(Severity.CRITICAL, "NGINX_DOMAIN", "Domain is not registered yet")
    with printer.section("Findings"):
        printer.finding(f)
    lines = capsys.readouterr().out.splitlines()
    assert lines[1] == "[x] NGINX_DOMAIN :: Domain is not registered yet"
