

#<-------------------------------------- Updater ------------------------------->
"""
This serves as an updater tool. It will be checking for updates whenever available and ask you to update to the latest version.
"""

#<--------------------- LIBS-------------------->
import requests
from rich.console import Console
import subprocess
from .config import *
import os
from datetime import datetime


# < ----------------------- Getting current dir --------------------------->
base_dir = os.path.dirname(os.path.abspath(__file__))
dir_of_data_file = base_dir + "/../data/last_update.txt"

console = Console()

data_file = os.path.abspath(dir_of_data_file)



def check_for_updates():
    with console.status(f"[{lblue}]Checking for updates ...[/{lblue}]"):
        config_version_url = "https://raw.githubusercontent.com/Nuksyn/scope/master/tools/config.py"
        try:
            data = requests.get(config_version_url)
        except Exception as e:
            console.print(f"[{error}]\\[x][/{error}] [{warning}]Could not reach GitHub to check for updates[/{warning}]")
            return


        raw = data.text
        if version in raw:
            console.print(f"[{green}][+][/{green}] [{lblue}]Already up to date![/{lblue}]")
        else:
            console.print(f"[{warning}][!][/{warning}] [{purple}]New update available, installing now...[/{purple}]")
            try:
                result = subprocess.run(["git", "pull"], capture_output=True, text=True)
                console.print(f"[{green}][+] Successfully updated to {version}![/{green}]")
                try:
                    with open(data_file, "w") as f:
                        f.write(datetime.now().strftime("%Y-%m-%d"))
                except Exception as e:
                    print("There was a problem writing to the file")
                return True





            except Exception as e:
                console.print(f"[{error}]\\[x][/{error}] [{warning}]Update failed![/{warning}]")
                return






def should_update() -> bool:
    try:
        with open(data_file, "r") as f:
            date_string = f.read().strip()
    except Exception as e:
        return True
    last_check = datetime.strptime(date_string, "%Y-%m-%d")
    current_time = datetime.now()
    diff = current_time - last_check
    if diff.days > 7:
        update = check_for_updates()
        if update:
            exit()

    else:
        return False



should_update()