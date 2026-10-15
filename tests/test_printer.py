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
