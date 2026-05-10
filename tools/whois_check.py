# --------------------- doc ------------------------ #
"""
Whois Lookup tool utilising whois lib
The tool performs domain checks, if no flags are parsed it does a full lookup of the domain,
available flags are --registrar --dates --dnssec --status --nameservers
"""

# --------------------- Import Librarries ------------------------ #
from rich.console import Console
import whois
import datetime

# -------- Import config file completely, don't change it's small and it makes it simpler to use colors ------- #
from config import *

# ---------- initialization of a console object for formatting ---------------- #
console = Console()
# ---------- initialization of a console object for formatting ---------------- #




def check_whois(domain:str, nameservers = None, registrar = None, dates = None, dnssec = None, status= None):
    #<----------------------------------- Preliminary checks ----------------------------->
    if domain == "":
        console.print(f"[{error}]\\[x][/{error}] {domain}:: [{warning}]Whois Lookup Failed[/{warning}]")
        return
    elif domain == None:
        console.print(f"[{error}]\\[x][/{error}] -- [{warning}]None is not accepted value![/{warning}]")
        return
    #<--------------------------------- Local vars ---------------------------------->

    all_flags = (nameservers, registrar, dates, dnssec, status)

    #<----------------------------------- Functions used by the tool ----------------->
    def whois_registrar(whois_information):
        registrar = whois_information.get("registrar")
        reseller_name = whois_information.get("reseller")
        whois_server = whois_information.get("whois_server")
        registrar_url = whois_information.get("registrar_url")
        if registrar:
            console.print(f"[{green}][+][/{green}] >> [{lblue}]{registrar}[/{lblue}]")
        else:
            console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Registrar Not Found[/{warning}]")
        if reseller_name:
            console.print(f"[{green}][+][/{green}] >> [{lblue}]{reseller_name}[/{lblue}]")
        else:
            console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Reseller Name Not Found[/{warning}]")
        if whois_server:
            console.print(f"[{green}][+][/{green}] >> [{lblue}]{whois_server}[/{lblue}]")
        else:
            console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Whois Server Not Found[/{warning}]")
        if registrar_url:
            console.print(f"[{green}][+][/{green}] >> [{lblue}]{registrar_url}[/{lblue}]")
        else:
            console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Registrar Url Not Found[/{warning}]")

    def whois_dates(whois_information):

        def handle_dates_whois_fix(value):
            if value is None:
                return None

            if isinstance(value, list):
                value = min(value)

            return value

        creation_date = whois_information.get("creation_date")  # fix none output
        if creation_date:
            creation_date = handle_dates_whois_fix(creation_date)
            console.print(f"[{green}][+] [{ice}]Creation Date[/{ice}] >> [/{green}] {creation_date}")
        else:
            console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Creation Date Not Found[/{warning}]")
        update_date = whois_information.get("updated_date")  # fix none output
        if update_date:
            update_date = handle_dates_whois_fix(update_date)
            console.print(f"[{green}][+] [{ice}]Update Date[/{ice}] >> [/{green}][{fog}]{update_date}[/{fog}]")
        else:
            console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Update Date not found[/{warning}]")
        expiration_date = whois_information.get("expiration_date")  # fix none output
        if expiration_date:
            expiration_date = handle_dates_whois_fix(expiration_date)
            console.print(f"[{green}][+] [{ice}]Expiration Date[/{ice}] >> [/{green}]{expiration_date}")
        else:
            console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Expiration Date Not Found[/{warning}]")

    # whois_dates(whois_information)

    def whois_nameservers(whois_information):
        nameservers = whois_information.get("name_servers")
        for name in nameservers:
            console.print(f"[{green}][+] == [/{green}][{lblue}]{name}[/{lblue}]")

    def whois_dnssec(whois_information):
        dnss_sec_status = whois_information.get("dnssec")
        console.print(f"[{green}][+] >> [/{green}][{purple}]{dnss_sec_status}[/{purple}]")

    def whois_status(whois_information):
        status_list = whois_information.get("status")
        if isinstance(status_list, list):
            for status in status_list:
                console.print(f"[{green}][+] >> [/{green}][{purple}]{status}[/{purple}]")
        else:
            console.print(f"[{green}][+] >> [/{green}][{purple}]{status_list}[/{purple}]")

    #<--------------------------------- Data Scrape --------------------------------->

    try:
        with console.status(f"[{lblue}]Performing a Whois Lookup...[/{lblue}]"):
            whois_information = whois.whois(domain)


            # whois_status(whois_information)
    except whois.exceptions.WhoisDomainNotFoundError:
        console.print(f"[{error}]\\[x][/{error}] [{warning}]{domain}[/{warning}] :: [{warning}]Domain Not Found[/{warning}]") # NEEDS COLOR
        return

    #<------------------------------ Main Logic --------------------------->

    # 1. If no flags run everything
    if not any(all_flags):
        whois_registrar(whois_information)
        whois_dates(whois_information)
        whois_nameservers(whois_information)
        whois_dnssec(whois_information)
        whois_status(whois_information)
    # 2. If dnssec flag exists
    if dnssec:
        whois_dnssec(whois_information)
    # 3. If status flag exists
    if status:
        whois_status(whois_information)
    # 4. If registrar flag exists
    if registrar:
        whois_registrar(whois_information)
    # 5. If dates flag exists
    if dates:
        whois_dates(whois_information)
    # 6. If ns flag exists
    if nameservers:
        whois_nameservers(whois_information)









#
check_whois("github.com")
check_whois("google.com")
check_whois("python.org")
check_whois("thisdomaindoesnotexist123456.com")
check_whois("https://google.com")
check_whois("")
check_whois(None)






