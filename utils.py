import csv
import os
from datetime import datetime

import requests


def init_data(file_path: str) -> list:
    with open(file_path, "r") as fi:
        result = fi.read().rstrip().split("\n")
    return result


def check_existing_files():
    dirs = ["subreddits"]
    files = ["errors.csv"]

    for dir in dirs:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    for fi in files:
        if not os.path.isfile(fi):
            os.mknod(fi)
        
        if fi == "errors.csv":
            with open("errors.csv", "w") as fi:
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