import os

from praw import Reddit

from processing import scan_subreddit
from utils import check_existing_files, read_config


def main():
    config = read_config()

    reddit = Reddit(config["bot_name"]) # put configuration from praw.ini here

    if not os.path.isfile("config.json"):
        print("Missing config.json. The script will terminate.")
        return
    
    subreddits = config["subreddits"]

    check_existing_files()

    for subreddit_name in subreddits:
        print(f"Scanning r/{subreddit_name}")
        scan_subreddit(reddit, subreddit_name)


if __name__ == "__main__":
    main()