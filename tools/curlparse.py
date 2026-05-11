# --------------------- doc ------------------------ #
"""

"""

# --------------------- Import Librarries ------------------------ #
from rich.console import Console
import requests
import time


# -------- Import config file completely, don't change it's small and it makes it simpler to use colors ------- #
from .config import *

# ---------- initialization of a console object for formatting ---------------- #
console = Console()
# ---------- initialization of a console object for formatting ---------------- #


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #this fixes the error message for not secure




def check_curl(domain:str, headers=None,cdn = None, redirects=None, cached=None, status_code=None,verbose=None, ttfb=None,uf=None, timeout=default_http_timeout):
    optional_flags = [headers, cdn, redirects, cached, status_code, verbose, ttfb, uf]
    #<------------------------------- preliminary checks ------------------------------>
    if domain == None:
        console.print(f"[{error}]\\[x][/{error}] -- [{warning}]Don't try to trick the software![/{warning}]")
        return
    if domain == "":
        console.print(f"[{error}]\\[x][/{error}] {domain}:: [{warning}]Empty string[/{warning}]")
        return
    if not domain.startswith("https://") and not domain.startswith("http://"):
        domain = "https://" + domain
    #<----------------------------------- Local vars -------------------------------------------->

    sg_dynamic_cached = "X-Proxy-Cache"
    sg_dynamic_cache_enabled = "X-Cache-Enabled"

    cf_hosted = "CF-RAY"
    sg_cdn_header = "X-SG-CDN"
    sg_cdn_header_premium = "X-CDN-C"
    sg_cdn_edge_location = "X-CE"


    uf_headers = "X-Httpd-Modphp"
    standard_php = "X-Httpd"

    #<---------------------------------- Performing A cURL -------------------------------------------->
    with console.status(f"[{fog}]Preliminary cURL Test...[/{fog}]"):
        try:
            data = requests.get(domain,verify=False, timeout=timeout, headers=headers_ua)

        except requests.exceptions.ConnectionError:
            console.print(f"[{error}]\\[x][/{error}] [{white}]::[/{white}] [{warning}]Does not exist or unreachable[/{warning}]")
            return
        except requests.exceptions.Timeout:
            console.print(f"[{error}]\\[x][/{error}] [{white}]::[/{white}] [{warning}]Timeout[/{warning}]")
            return
        except requests.exceptions.TooManyRedirects:
            console.print(f"[{error}]\\[x][/{error}] [{white}]::[/{white}] [{warning}]Too many redirects error[/{warning}]")
            return
        except Exception as e:
            console.print(f"[{error}]\\[x][/{error}] [{white}]::[/{white}] [{warning}]Generic Error[/{warning}]")
            return

    def curl_status(data):
        console.print(f"[{ice}]── [{purple}]Status[/{purple}] ────────────────────────────────────[{ice}]")
        status_code = data.status_code
        location = data.url
        captcha = False

        if status_code == 202:
            captcha = True
        history = data.history

        if history:
            for item in history:
                console.print(f"{status_sign(item.status_code)} >> [{purple}]{item.status_code}[/{purple}] >> [{lblue}]{item.url}[/{lblue}]")
        if captcha:
            console.print(f"[{warning}][!][/{warning}] >> [{warning}]SG-CAPTCHA DETECTED![/{warning}]")## <---------------------- colouring needed
        console.print(f"{status_sign(status_code)} >> [{purple}]{status_code}[/{purple}] >> [{lblue}]{location}[/{lblue}]")






    def curl_cache(data):
        console.print(f"[{ice}]── [{purple}]Cache[/{purple}] ────────────────────────────────────[{ice}]")
        counter = 0
        headers = data.headers
        if sg_dynamic_cached in headers:
            if headers[sg_dynamic_cached] == "HIT":
                icon = f"[{green}][+][/{green}]"
            else:
                icon = f"[{error}]\\[x][/{error}]"
            console.print(f"{icon} >> [{lblue}]X-Proxy-Cache : {headers[sg_dynamic_cached]}[/{lblue}]")
            counter+=1
        if sg_dynamic_cache_enabled in headers:
            if headers[sg_dynamic_cache_enabled] == "True":
                icon = f"[{green}][+][/{green}]"
            else:
                icon = f"[{error}]\\[x][/{error}]"
            console.print(f"{icon} [{lblue}]X-Cache-Enabled : {headers[sg_dynamic_cache_enabled]}[/{lblue}]")
            counter+=1
        if counter == 0:
            console.print(f"[{error}]\\[x][/{error}] [{warning}]No SiteGround Caching Headers Found[{warning}]")



    def curl_cdn(data):
        console.print(f"[{ice}]── [{purple}]CDN[/{purple}] ────────────────────────────────────[{ice}]")
        headers = data.headers
        is_premium = ""
        if sg_cdn_header in headers:
            if sg_cdn_header_premium in headers:
                is_premium = f"[{lblue}]Premium [/{lblue}]"

            console.print(f"[{green}][+][/{green}] [{lblue}]SiteGround {is_premium}CDN Detected![/{lblue}]")
            if sg_cdn_edge_location in headers:
                console.print(f"[{green}][+][/{green}] [{purple}]{headers[sg_cdn_edge_location]} edge served this request[/{purple}]")

        elif cf_hosted in headers:
            console.print(f"[{warning}][!][/{warning}] [{purple}]CloudFlare CDN Detected![/{purple}]")

        else:
            console.print(f"[{error}]\\[x][/{error}] [{warning}]No known CDN detected![/{warning}]")

    def curl_uf(data):
        console.print(f"[{ice}]── [{purple}]UF PHP Checker[/{purple}] ────────────────────────────────────[{ice}]")
        headers = data.headers
        if uf_headers in headers:
            console.print(f"[{green}][+][/{green}] [{lblue}]UltraFast PHP is Enabled![/{lblue}]")
        elif standard_php in headers:
            console.print(f"[{warning}][!][/{warning}] [{ice}]Standard PHP is Enabled![/{ice}]")
        else:
            console.print(f"[{error}]\\[x][/{error}] [{fog}]Can't determine the type of php![/{fog}]")



    def curl_headers(data):
        hops = 0
        console.print(f"[{ice}]── [{purple}]Headers[/{purple}] ────────────────────────────────────[{ice}]")
        headers = data.headers
        headers_history = data.history
        if headers_history:
            for itemz in headers_history:
                hops += 1
                old_headers = itemz.headers
                console.print(f"[{ice}]── [{purple}]Hop {hops}[/{purple}] ────────────────────────────────────[{ice}]")
                for key,item in old_headers.items():

                    console.print(f"[{green}][+][/{green}] [{lblue}]{key} :: {item}[/{lblue}]")
        hops += 1
        console.print(f"[{ice}]── [{purple}]Hop {hops}[/{purple}] ────────────────────────────────────[{ice}]")
        for keyz,valuez in headers.items():
            console.print(f"[{green}][+][/{green}] [{lblue}]{keyz} :: {valuez}[/{lblue}]")


    def curl_cached_retry(domain):
        counter = 0 #max counter is 10, Loop closes on 10
        counter_cache = 0 #this tracks the % of cached
        console.print(f"[{ice}]── [{purple}]Cache Testing[/{purple}] ────────────────────────────────────[{ice}]")
        with console.status(f"[{fog}]cURL...[/{fog}]"):
            try:
                while counter < 11:
                    try:
                        data = requests.get(domain, verify=False, timeout=timeout, headers=headers_ua)
                    except Exception as e:
                        console.print(f"[{error}]\\[x][/{error}] {e}!")
                        return
                    headers = data.headers
                    if sg_dynamic_cached in headers:
                        if headers[sg_dynamic_cached] == "HIT":
                            counter_cache += 1
                            console.print(f"[{green}][+][/{green}] >> [{lblue}]HIT[/{lblue}]")
                        elif headers[sg_dynamic_cached] == "MISS":
                            console.print(f"[{warning}]\\[!][/{warning}] >> [{warning}]MISS[/{warning}]")
                        else:
                            console.print(f"[{error}]\\[x][/{error}] >> [{warning}]No SG-Cache Info[/{warning}]")

                    counter += 1
                console.print(f"[{purple}][*][{purple}][{ice}] {round((counter_cache / 10) * 100)}% of the requests were cached by SiteGround server[/{ice}]")
            except Exception as e:
                console.print(f"[{error}]\\[x][/{error}] {e}!")
                return
    def curl_ttfb(domain):
        console.print(f"[{ice}]── [{purple}]TTFB[/{purple}] ────────────────────────────────────[{ice}]")
        start = time.perf_counter()
        with console.status(f"[{fog}]cURL...[/{fog}]"):
            try:
                requests.get(domain, verify=False, timeout=default_http_timeout, headers=headers_ua)
            except Exception as e:
                console.print(f"[{error}]\\[x][/{error}] {e}!")
                return
            end = time.perf_counter()

            total = end - start
            console.print(f"[{green}][+][/{green}] [{purple}]{total:.2f} seconds to first byte[/{purple}]")


    # <----------------------------------------- Main Logic ------------------------------------>

    #1. If no flags are parsed print basic info
    if not any(optional_flags):
        curl_status(data)
        curl_cache(data)
        curl_cdn(data)
        curl_uf(data)
    if headers:
        curl_headers(data)
    if cdn:
        curl_cdn(data)
    if cached:
        curl_cache(data)
        curl_cached_retry(domain)
    if status_code:
        curl_status(data)
    if verbose:
        curl_status(data)
        curl_cache(data)
        curl_cdn(data)
        curl_uf(data)
        curl_headers(data)
        curl_cached_retry(domain)
        curl_ttfb(domain)
    if ttfb:
        curl_ttfb(domain)
    if uf:
        curl_uf(data)


