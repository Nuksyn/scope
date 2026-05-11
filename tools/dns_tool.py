# --------------------- doc ------------------------ #
"""
DNS resolver
offers utilities such as parsing flags that work stand-alone --ptr, --spf, --dmarc, --caa as well as if you add separate valid records --record.
If no  flags are offered the tool will automatically do a full recon
supports --ptr x.x.x.x reverse lookups
"""
# --------------------- Import Librarries ------------------------ #
from rich.console import Console
import dns.resolver
from typing import List

# -------- Import config file completely, don't change it's small and it makes it simpler to use colors ------- #
from config import *


# ---------- initialization of a console object for formatting ---------------- #
console = Console()
# ---------- initialization of a console object for formatting ---------------- #

def check_dns(domain:str = None, record: List[str] = None, resolver: List[str] = None, ptr: str = None,spf:bool = False, dmarc: bool = False, caa: bool = False):
    # ------------------------------ variables  ------------------------------ #
    optional_arguments = [spf,dmarc,caa] #create a list of optionals
    flags = (spf, dmarc, caa, ptr, record) #patch var for the last condition with no flags parsed
    # <------------------------- Preliminary checks for flag conflicts -------------------------> #
    if ptr and spf or ptr and dmarc or ptr and any(optional_arguments) or ptr and caa:
        console.print(f"[{error}]Not allowed to use PTR with other flags![/{error}]")
        return
    # ---------------- < Creating a resolver if flag is parsed > ------------------------- #

    dns_resolver = dns.resolver.Resolver() #create a resolver object

    if resolver:
        dns_resolver.nameservers = resolver # < --- this is a list, loop over later

    # <------------------------- Preliminary checks for resolution-------------------------> #
    if not domain and not ptr:
        console.print(f"[{error}]\\[x][/{error}] :: [{warning}]No domain provided[/{warning}]")
        return

    with console.status(f"[{purple}]Resolving...[/{purple}]"):
        if not ptr:
            try:
                preliminary = dns_resolver.resolve(domain, "NS")
            except dns.resolver.LifetimeTimeout:
                console.print(f"[{error}]\\[x][/{error}][{fog}]Timeout[/{fog}] :: [{warning}]DNS lookup timed out[/{warning}]")
                return
            except dns.resolver.NXDOMAIN:
                console.print(f"[{error}]\\[x] NXDOMAIN[/{error}] :: [{warning}]domain [{purple}]{domain}[/{purple}] does not exist[/{warning}]")
                return
            except dns.resolver.NoAnswer:
                console.print(f"[{error}]\\[-][/{error}] [{purple}]{domain}[/{purple}] :: [{warning}]No active DNS zone detected[/{warning}]")
                return


    # <-------------------- Dealing with the actual resolving ---------------> #
    def check_record(domain:str, record_type:str):
        with console.status(f"[{purple}]Resolving...[/{purple}]"):
            #<----------------- Tries to resolve record----------------->
            try:
                answers = dns_resolver.resolve(domain, record_type)
                for answer in answers: #just for output
                    console.print(f"[{green}][+][/{green}] [{fog}]{record_type}[/{fog}] :: [{ice}]{answer}[/{ice}]") # just for output


            #<------------------------- Inner Excepts  --------------------
            except dns.resolver.NoAnswer:
                console.print(f"[{error}]\\[-][/{error}] [{purple}]{record_type} type[/{purple}] :: [{warning}]Not found[/{warning}]")
            except dns.rdatatype.UnknownRdatatype:
                console.print(
                    f"[{error}]\\[x][/{error}] [purple]{record_type}[/purple] [{error}]UNKNOWN[/{error}] :: [{warning}]unknown record type[/{warning}]")
    #<-----------------------------Just Cosmetic Header -------------------------->
    # print('********************************')
    # print(f"\t\tDNS — {domain}")
    # print('********************************')
    #        NEEDS REWORK VERY UGLY
    #<----------------------------- Main Logic ----------------------->
    # 1. PTR

    if ptr:
        console.print(f"[{ice}]── [{purple}]PTR[/{purple}] ────────────────────────────────────[{ice}]")
        try:
            reverse_ip_list = ptr.split('.')
            reversed_record = '.'.join(reverse_ip_list[::-1]) + ".in-addr.arpa"
            ptr_record = dns.resolver.resolve(reversed_record, "PTR")
            for answer in ptr_record:
                console.print(f"[{ice}]{answer.target}[/{ice}]")
            return
        except Exception:
            console.print(f"[{error}]\\[x][{error}] [{warning}]No PTR record found[{warning}]")
            return

    # 2. SPF
    if spf:
        console.print(f"[{ice}]── [{purple}]SPF[/{purple}] ────────────────────────────────────[/{ice}]")
        answers = dns_resolver.resolve(domain, "TXT")
        for answer in answers:
            if "v=spf1" in str(answer):
                console.print(answer)

    # 3. DMARC

    if dmarc:
        console.print(f"[{ice}]── [{purple}]DMARC[/{purple}] ────────────────────────────────────[/{ice}]")
        dmarc_domain = "_dmarc." + domain
        check_record(dmarc_domain,"TXT")
    # 4. CAA
    if caa:
        console.print(f"[{ice}]── [{purple}]CAA[/{purple}] ────────────────────────────────────[/{ice}]")
        check_record(domain, "CAA")
    # 5. One or more records
    if record:
        for rec in record:
            console.print(f"[{ice}]── [{purple}]{rec}[/{purple}] ────────────────────────────────────[/{ice}]")
            check_record(domain,rec.upper())

    if not any(flags):
        for rec in default_records_for_dns:

            console.print(f"[{ice}]── [{purple}]{rec}[/{purple}] ────────────────────────────────────[/{ice}]")

            check_record(domain, rec)




#TEESTS

check_dns("https://googleasdasdsa.com")                    # all recs
check_dns("google.com")
check_dns("cloudflare.com")
check_dns("example.com")
check_dns("google.com", spf=True)
check_dns("gmail.com", spf=True)

check_dns("google.com", dmarc=True)
check_dns("example.com", dmarc=True)

check_dns("google.com", caa=True)
check_dns("example.com", caa=True)
check_dns("google.com", record=["a", "mx"])
check_dns("cloudflare.com", record=["txt", "ns"])
check_dns("example.com", record=["AAAA", "MX", "TXT"])
check_dns(ptr="8.8.8.8")
check_dns(ptr="1.1.1.1")
check_dns(ptr="8.8.4.4")
check_dns("google.com", ptr="8.8.8.8", spf=True)
check_dns("google.com", ptr="8.8.8.8", dmarc=True)
check_dns("google.com", ptr="8.8.8.8", caa=True)
check_dns("google.com", resolver=["1.1.1.1"])
check_dns("google.com", resolver=["8.8.8.8"])
check_dns("google.com", resolver=["9.9.9.9", "1.1.1.1"])
check_dns("google.com", record=["banana"])
check_dns("google.com", record=["email"])
check_dns("google.com", record=["xyz"])
check_dns("thisdomaindoesnotexist12345.com")
check_dns("fake-domain-test.invalid")
check_dns("google.com", resolver=["0.0.0.0"])
check_dns("google.com", spf=True, dmarc=True, caa=True)
check_dns("google.com", record=["MX", "A"], spf=True, caa=True)
check_dns("")
check_dns(None)
check_dns("google.com", record=[])