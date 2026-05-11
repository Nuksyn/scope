

#<-------------------------------------- Updater ------------------------------->
"""
This serves as an updater tool. It will be checking for updates whenever available and ask you to update to the latest version.
"""

#<--------------------- LIBS-------------------->
import requests
from rich.console import Console
import subprocess
from config import *


console = Console()
def check_for_updates():
    with console.status("Checking for updates ..."):
        config_version_url = "https://raw.githubusercontent.com/Nuksyn/scope/master/tools/config.py"

        try:
            data = requests.get(config_version_url)
        except Exception as e:
            print("Something went wrong")
            return


        raw = data.text
        if version in raw:
            print("This version is already up-to-date")
        else:
            print("New update available, installing now!")
            try:
                result = subprocess.run(["git", "pull"], capture_output=True, text=True)
                print(result.stdout)
                print(result.returncode)
            except Exception as e:
                print("Something went wrong")
                return
check_for_updates()