import csv
import os

from praw import Reddit

from utils import download_media, get_csv_column, has_gallery, now_timestamp


def scan_subreddit(reddit: Reddit, subreddit_name: str, limit: int = 10):
    subreddit_path = f"subreddits/{subreddit_name}"
    posts_path = f"{subreddit_path}/posts_{subreddit_name}.csv"
    errors_path = "errors.csv"

    if not os.path.isdir(subreddit_path): # check if dir exists
        os.mkdir(subreddit_path)
        os.mknod(posts_path)

        with open(posts_path, "w") as fi:
            fi.write("id;user;title;timestamp\n")

    existing_ids = get_csv_column(posts_path, "id") + get_csv_column(errors_path, "id")

    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.new(limit=limit):
        if submission.id in existing_ids:
            print(f"Skipping {submission.id}")
            continue

        try:
            if has_gallery(submission):
                print(f"Processing gallery {submission.id}")
                process_gallery(submission, subreddit_name)
            else:
                if not submission.is_self:
                    print(f"Processing media {submission.id}")
                    process_media(submission, subreddit_name)
                else:
                    print(f"Processing self {submission.id}")
                    process_self(submission, subreddit_name)

            add_to_posts(submission, subreddit_name)
        except Exception as e:
            add_error(submission, e)


def process_gallery(submission, subreddit_name: str):
    items = submission.gallery_data["items"]
    meta = submission.media_metadata

    for idx, item in enumerate(items, start=1):
        media_id = item["media_id"]
        media_url = meta[media_id]["s"]["u"]

        extension = media_url.split(".")[-1].split("?")[0]
        output_name = f"{submission.id}_{idx}.{extension}"
        output_path = f"subreddits/{subreddit_name}/{output_name}"

        download_media(media_url, output_path)


def process_media(submission, subreddit_name: str):
    extension = submission.url.split(".")[-1]
    output_name = f"{submission.id}.{extension}"
    output_path = f"subreddits/{subreddit_name}/{output_name}"

    download_media(submission.url, output_path)


def process_self(submission, subreddit_name: str):
    output_name = f"{submission.id}.md"
    output_path = f"subreddits/{subreddit_name}/{output_name}"

    with open(output_path, "w") as fi:
        fi.write(submission.selftext)


def add_to_posts(submission, subreddit_name: str):
    posts_path = f"subreddits/{subreddit_name}/posts_{subreddit_name}.csv"
    with open(posts_path, "a", newline="") as csvfile:
        row = [
            submission.id, submission.author.name, submission.title, now_timestamp()
        ]

        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(row)


def add_error(submission, description: str):
    with open("errors.csv", "a", newline="") as csvfile:
        row = [
            submission.id, now_timestamp(), description
        ]

        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(row)