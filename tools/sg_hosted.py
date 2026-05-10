# --------------------- doc ------------------------ #
"""
This is functionality that will both return a True
if the domain is hosted by SiteGround and will print it
Make sure to run prior to tools that are dependent on "sg_hosted" as they might be utilizing it for the flag
"""
# --------------------- Import Librarries ------------------------ #
from rich.console import Console
import requests
import re

# ------------------------- Import of not-mandatory Libs -------------------------#
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #this fixes the error message for not secure
#because we are using verify=False in the get request

# -------- Import config file completely, don't change it's small and it makes it simpler to use colors ------- #
from config import *

# ---------- initialization of a console object for formatting ---------------- #
console = Console()

#---------------- patch for the incorrect format of domain handling ----------------- #


pattern = r"^https?://([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}/\.well-known/sg-hosted-ping\\?$" # do not edit, instead add more edge case rules


# ----------------

def check_sg_hosted(domain:str) -> bool:
    """
    This is a function that deals with checking if the domain is hosted by SiteGround
    The function deals with ensuring the domain format is correct for the requests library
    :param domain: always a string
    :return: True or False and prints before exiting the function
    """
    # ------------------- Must not delete variables --------------------- #
    nginx_location_list = [] # if this var is deleted the except block will crash as
    # it's checking the list for entries and it will never get created down the line

    with console.status("Transforming data ..."):
        # Case 1: Missing Protocol

        if not domain.startswith("https://") and not domain.startswith("http://"):
            domain = "https://" + domain

        # Case 2: Adding trailing slash if missing

        if not domain.endswith("/"):
            domain = domain + "/"
        # ----------------- Adding nginx location to the path ----------------------- #
        domain = domain + ".well-known/sg-hosted-ping"



    # -------------------- Ensuring that the domain always is in the correct format for requests -------------------- #
    # NB! This must ALWAYS be right before the executable code under the main sequence
    with console.status(f"[{purple}]Matching Reggex ...[{purple}]"):
        if not re.search(pattern, domain):
            console.print(f"[{error}]\\[x][/{error}] [{warning}]Not supported format.[/{warning}]")
            console.print(f"[{warning}]Please use the following format:[/{warning}] [{fog}]domain.com, www.domain.com, http://domain.com, https://domain.com[/{fog}]")
            return False

    # ------------------- Must not delete variables --------------------- #
    nginx_location_list = [] # if this var is deleted the except block will crash as
    # it's checking the list for entries and it will never get created down the line

    with console.status(f"[{purple}]Resolving...[/{purple}]"):
        try:
            answer = requests.get(domain, verify=False, timeout=default_http_timeout, headers=headers)
            nginx_location_list = answer.text.split()
            pong = nginx_location_list[2]
            server = nginx_location_list[1]
            domain = nginx_location_list[0]
            # ------------- Checking if it's hosted here------------ #
            if pong == "pong":
                console.print(f"[{green}][+][/{green}] [{white}]::[/{white}] [{green}]Hosted on SiteGround[/{green}]")
                console.print(f"[{green}][+][/{green}] [{white}]::[/{white}] [{ice}]Hosting server:[/{ice}] [{purple}]{server}[/{purple}]")
                # -------------- Checking if the username starts with alphanumeric characters ------------ #
                if domain[0].isalnum():
                    console.print(f"[{green}][+][/{green}] [{white}]::[/{white}] [{ice}]Server username:[/{ice}] [{purple}]{domain}[/{purple}]")
                else:
                    console.print(f"[{warning}][!][/{warning}] [{white}]::[/{white}] [{warning}]Username seems off > {domain}[/{warning}]")
            else:
                console.print(f"[{error}]\\[x][/{error}] [{white}]::[/{white}] [{warning}]Not hosted on SiteGround[/{warning}]")
                return False
            return True
        except requests.exceptions.ConnectionError:
            console.print(f"[{error}]\\[x][/{error}] [{white}]::[/{white}] [{warning}]Does not exist or unreachable[/{warning}]")
            return False


        except Exception as the_error:
            if nginx_location_list and "pong" in nginx_location_list and isinstance(the_error, IndexError):
                console.print(f"[{warning}][!][/{warning}] [{white}]::[/{white}] [{warning}]Might be SG hosted but something is wrong[/{warning}]")
            else:
                console.print(f"[{error}]\\[x][/{error}] [{white}]::[/{white}] [{warning}]Not hosted on SiteGround[/{warning}]")
            return False




# <------------------------------------ Tests -----------------------------------> #

# print('Test 1: Expected result -> Hosted on SiteGround')
# check_sg_hosted("journeyofvitality.com") # Should return hosted
# print('Test 2: Expected result -> Not Hosted on SiteGround')
# check_sg_hosted("google.com") #Should return not hosted
# print('Test 3: Expected result -> Not Supported Format')
# check_sg_hosted("//asdasdasdasdasdsadas.com")  # should return incorrect format
# print("Test 4: Expected result -> Does not Exist or Unreachable")
# check_sg_hosted("asdasdasdasdasdsadas.com")  # should return does not exists

# <----------------------------------End of Tests -----------------------------------> #


