version = "0.2.0-alpha"   #### Edit version to something custom to stop auto-updates (DONT RECOMMEND AT ALL)
#if you want to re-enable auto-updates after that you will need to manually go to the folder of the script
# and perform "git checkout ." and then force an update with "git pull"
#<-------------------------- Config file -------------------------->
"""
This is config file, DO NOT edit unless you know what you are doing.
Here you can control the UA, the available colors and global headers used for the "requests" library, as well as timeout limits.
"""

#<-------------------------- Config file -------------------------->)

#<-------------------------- UA  -------------------------->
user_agent = f"SGScope/{version} (SiteGround Support Recon Tool)" #You can edit this part as long as it stays a string and is not something mod_sec will trigger
#<-------------------------- UA  -------------------------->
#
#<------------------------------- Global Libraries ---------------------------------->

import urllib3

#<------------------------------------ Global features ------------------------------------->
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #this fixes the error message for not secure

#<-------------------------- Start of Colors -------------------------->
#This is a default palletre, feel welcome to add more or edit the code of existing if you wish, but be careful to not break prints with incorrect ones
ice   = "#6CA8D9"   # field labels
blue  = "#00E5FF"   # main values
white  = "#FFFFFF"   # general text
fog  = "#8DA1B3"   # secondary info
purple      = "#BD93F9"   # section headers
green       = "#50FA7B"   # confirmed success
warning     = "#FFB86C"   # warnings
error       = "#FF5555"   # errors
lblue  = "#8BE9FD"   # informational [*]
#<-------------------------- End of Colors -------------------------->


#<-------------------------- Start of Global Settings -------------------------->
default_http_timeout = 10
default_ssl_timeout = 10
#<-------------------------- End of Global Settings -------------------------->


#<-------------------------- headers for requests -------------------------->
headers_ua = {
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}
#<-------------------------- End of headers -------------------------->

default_records_for_dns = ["A", "AAAA", "MX", "NS", "TXT", "DS", "CAA"] #adding or removing more records here may break the dns tool


okay_codes = [200, 201, 202, 204, 206]
warning_codes = [301, 302, 307, 308, 401, 403, 405, 408, 409, 429]
error_codes = [400, 404, 410, 500, 501, 502, 503, 504, 505]
def status_sign(status_code):
    sign = ''
    if status_code in okay_codes:
        sign = f"[{green}][+][/{green}]"
    elif status_code in warning_codes:
        sign = f"[{warning}][!][/{warning}]"
    elif status_code in error_codes:
        sign = f"[{error}]\\[x][/{error}]"
    return sign



