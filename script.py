import os

from praw import Reddit

from processing import scan_subreddit
from utils import check_existing_files, init_data


def main():
    reddit = Reddit("gudin") # put configuration from praw.ini here

    if not os.path.isfile("subreddits.txt"):
        print("Missing subreddits.txt. The script will terminate.")
        return
    
    subreddits = init_data("subreddits.txt")

    check_existing_files()

    for subreddit_name in subreddits:
        print(f"Scanning r/{subreddit_name}")
        scan_subreddit(reddit, subreddit_name)


if __name__ == "__main__":
    main()