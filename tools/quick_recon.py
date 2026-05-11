# --------------------- doc ------------------------ #
"""

"""

# --------------------- Import Librarries ------------------------ #
from rich.console import Console
# -------- Import config file completely, don't change it's small and it makes it simpler to use colors ------- #
from .config import *
from .curlparse import *
from .sg_hosted import *
from .ssl_check import *
from .whois_check import *
from .dns_tool import *


# ---------- initialization of a console object for formatting ---------------- #
console = Console()
# ---------- initialization of a console object for formatting ---------------- #


def quick_scope(domain):
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    console.print(f"\t\t\t[{lblue}]◈ SG HOSTED ◈[/{lblue}]")
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    check_sg_hosted(domain)
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    console.print(f"\t\t\t[{lblue}]◈ Check DNS ◈[/{lblue}]")
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    check_dns(domain, record=["A","MX","TXT","AAAA"])
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    console.print(f"\t\t\t[{lblue}]◈ Check SSL ◈[/{lblue}]")
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    check_ssl(domain)
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    console.print(f"\t\t\t[{lblue}]◈ Curl Test ◈[/{lblue}]")
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    check_curl(domain)
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    console.print(f"\t\t\t[{lblue}]◈ WhoIS Information ◈[/{lblue}]")
    console.print(f"[{blue}]══════════════════════════════════════════════════════════════════════[/{blue}]")
    check_whois(domain, registrar=True,dates=True)


