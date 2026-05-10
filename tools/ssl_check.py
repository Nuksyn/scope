# --------------------- doc ------------------------ #
"""

"""

# --------------------- Import Librarries ------------------------ #
import ssl
import socket
import pprint
import datetime
from rich.console import Console

# -------- Import config file completely, don't change it's small and it makes it simpler to use colors ------- #
from config import *

# ---------- initialization of a console object for formatting ---------------- #
console = Console()
# ---------- initialization of a console object for formatting ---------------- #




def check_ssl(domain:str, cipher = None, expiry = None, issuer = None, sans = None, timeout=default_ssl_timeout):
    cert = None
    algo = None
    #<----------------- Preliminary Checks -------------------->


    #<--------------------- Main Engine ----------------->
    with console.status(f"[{fog}]TLS HandShake...[/{fog}]"):
        try:
            context = ssl.create_default_context()

            with (context.wrap_socket(
                    socket.create_connection((domain, 443), timeout=timeout),
                    server_hostname=domain,
            ) as s):
                cert = s.getpeercert()
                algo = s.cipher()
        except ssl.SSLCertVerificationError:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                console.print(f"[{warning}]\\[!][/{warning}] >> [{warning}]Self-signed or unverified certificate detected[/{warning}]")
                with (context.wrap_socket(
                        socket.create_connection((domain, 443), timeout=timeout),
                        server_hostname=domain,
                ) as s):
                    cert = s.getpeercert()
                    algo = s.cipher()
                    if 0 == len(cert):
                        return
            except Exception as e:
                console.print(f"[{error}]\\[x][/{error}] >> [{warning}]Hard unknown Error[/{warning}]")
        except socket.timeout:
            console.print(f"[{error}]\\[x][/{error}] >> [{warning}]Timeout[/{warning}]")
        except Exception as e:
            console.print(f"[{error}]\\[x][/{error}] >> [{warning}]Hard unknown Error[/{warning}]")
            return


    def ssl_cipher(algo):
        console.print(f"[{ice}]── [{purple}]SSL Ciphers[/{purple}] ────────────────────────────────────[{ice}]")
        for item in algo:

            console.print(f"[{green}][+][/{green}] [{purple}]{item}[/{purple}]")



    def ssl_expiry(cert):
        now = datetime.datetime.now().replace(microsecond=0)
        registration_date = datetime.datetime.strptime(cert.get("notBefore"), "%b %d %H:%M:%S %Y %Z")
        expiration_date = datetime.datetime.strptime(cert.get("notAfter"), "%b %d %H:%M:%S %Y %Z")
        console.print(f"[{ice}]── [{purple}]SSL Date Info[/{purple}] ────────────────────────────────────[{ice}]")
        console.print(f"[{green}][+][/{green}] [{ice}]Registration date:[/{ice}] [{lblue}]{registration_date}[/{lblue}]") # needs color
        console.print(f"[{green}][+][/{green}][{ice}] Expiration date:[/{ice}][{lblue}] {expiration_date}[/{lblue}]") # needs color
        console.print(f"[{green}][+][/{green}] [{ice}]Local time:[/{ice}] [{lblue}]{now}[/{lblue}]") # needs color
        diff = int((expiration_date - now).days)
        console.print(f"[{green}][+][/{green}] [{ice}]{diff}[{ice}] [{lblue}]days remaining to expiration[/{lblue}]") if diff > 30 else console.print(f"[{warning}]\\[!][/{warning}] >> [{fog}]Warning [{purple}]{diff}[/{purple}] days remaining[/{fog}]") # needs color


    def ssl_issuer(cert):
        for item in cert["issuer"]:
            console.print(f"[{ice}]── [{purple}]Issuer Details[/{purple}] ────────────────────────────────────[{ice}]")
            for key, value in item:
                console.print(f"[{green}][+][/{green}] [{ice}]{key}[/{ice}] :: [{lblue}]{value}[/{lblue}]") # add color



    def ssl_sans(cert):
        console.print(f"[{ice}]── [{purple}]SANS[/{purple}] ────────────────────────────────────[{ice}]")
        for key, item in cert["subjectAltName"]:
            console.print(f"[{green}][+][/{green}] [{ice}]{key}[/{ice}] :: [{lblue}]{item}[/{lblue}]")


    # <---------------- Check if no flags --------------- >
    if not any([cipher, expiry, issuer, sans]):
        ssl_issuer(cert)
        ssl_expiry(cert)
        ssl_cipher(algo)
        ssl_sans(cert)
    if cipher:
        ssl_cipher(algo)
    if expiry:
        ssl_expiry(cert)
    if issuer:
        ssl_issuer(cert)
    if sans:
        ssl_sans(cert)



