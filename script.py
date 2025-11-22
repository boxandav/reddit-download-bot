import os

from praw import Reddit

from processing import scan_redditor, scan_subreddit
from utils import check_existing_files, read_config


def main():
    config = read_config()

    reddit = Reddit(config["bot_name"]) # put configuration from praw.ini here

    if not os.path.isfile("config.json"):
        print("Missing config.json. The script will terminate.")
        return
    
    post_limit = config["post_limit"]
    subreddits = config["subreddits"]
    redditors = config["redditors"]

    check_existing_files()

    for subreddit_name, mode in subreddits.items():
        print(f"Scanning r/{subreddit_name}")
        scan_subreddit(reddit, subreddit_name, mode, post_limit)
    for redditor_name, mode in redditors.items():
        print(f"Scanning u/{redditor_name}")
        scan_redditor(reddit, redditor_name, mode, post_limit)


if __name__ == "__main__":
    main()