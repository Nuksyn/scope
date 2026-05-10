#<-------------------------- Config file -------------------------->
"""
This is config file, DO NOT edit unless you know what you are doing.
"""
#<-------------------------- Config file -------------------------->)

#<-------------------------- UA  -------------------------->
user_agent = "SGScope/0.1.0-alpha (SiteGround Support Recon Tool)" #You can edit this part as long as it stays a string and is not something mod_sec will trigger
#<-------------------------- UA  -------------------------->



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
default_records_for_dns = ["A", "AAAA", "MX", "NS", "TXT", "DS", "CAA"] #adding more records here may break the dns tool
default_ssl_timeout = 10
#<-------------------------- End of Global Settings -------------------------->


#<-------------------------- headers for requests -------------------------->
headers = {
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}
#<-------------------------- End of headers -------------------------->



