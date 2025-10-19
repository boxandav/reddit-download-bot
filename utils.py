import csv
import json
import os
from datetime import datetime

import requests


def read_config() -> dict:
    try:
        with open("config.json", "r") as fi:
            return json.load(fi)
        
    except FileNotFoundError:
        print("Missing config.json.")
        return {}
    except json.JSONDecodeError:
        print("Content of config.json is invalid.")
        return {}
    except Exception:
        print("Error while opening config.json.")
        return {}


def check_existing_files():
    config = read_config()
    locations = config["locations"].values()

    for location in locations:
        is_file = "." in location # file or directory

        if not is_file and not os.path.isdir(location):
            os.mkdir(location)
        
        if is_file:
            if not os.path.isfile(location):
                os.mknod(location)
            
            if location == config["locations"]["errors"]:
                with open(config["locations"]["errors"], "w") as fi:
                    fi.write("id;timestamp;description\n")


def has_gallery(subreddit) -> bool:
    if subreddit.is_self:
        return False
    
    try: # in the PRAW library the attribute seems to exist only for some submissions..
        result = subreddit.is_gallery
    except:
        result = False

    return result


def download_media(url: str, output_name: str):
    response = requests.get(url)
    if response.status_code == 200:
        extension = url.split(".")[-1]
        with open(output_name, "wb") as fi:
            fi.write(response.content)


def now_timestamp() -> str:
    now = datetime.now()
    timestamp = now.strftime("%d.%m.%Y %H:%M:%S")

    return timestamp


def get_csv_column(path: str, column: str) -> list:
    values = []
    with open(path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            values.append(row[column])
    
    return values