from dataclasses import FrozenInstanceError

import pytest

from domainscope.helpers.findings import Severity, Finding
from domainscope.helpers.printer import Status



def test_finding_stores_fields():
    """A Finding keeps the severity, code and message it was given."""
    finding = Finding(Severity.INFO, "NS_THIRD_PARTY", "Nameservers are at Cloudflare")
    assert finding.severity == Severity.INFO
    assert finding.code == "NS_THIRD_PARTY"
    assert finding.message == "Nameservers are at Cloudflare"


@pytest.mark.parametrize("bad_severity", ["hello", Status.FAIL, 0, 0.5, None, [], {}])
def test_finding_rejects_wrong_severity_type(bad_severity):
    """Anything that isn't a Severity raises TypeError."""
    with pytest.raises(TypeError):
        Finding(bad_severity, "CODE", "message")

def test_finding_is_frozen():
    """Changing a field after creation raises FrozenInstanceError."""
    finding = Finding(Severity.INFO, "NS_THIRD_PARTY", "Nameservers are at Cloudflare")
    with pytest.raises(FrozenInstanceError):
        # noinspection PyDataclass
        finding.severity = Severity.CRITICAL

def test_severity_values_order():
    """Severity values go INFO < WARNING < CRITICAL"""
    assert Severity.INFO.value < Severity.WARNING.value < Severity.CRITICAL.value
