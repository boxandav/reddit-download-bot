import csv
import os

from praw import Reddit

from utils import \
    download_media, get_csv_column, has_gallery, now_timestamp, read_config


config = read_config()
dir_locations = {
    "subreddit": config["locations"]["subreddits_dir"],
    "redditor": config["locations"]["redditors_dir"]
}
errors_loc = config["locations"]["errors"]
save_posts = config["save_posts"]


def scan_subreddit(reddit: Reddit, subreddit_name: str, limit: int = 10):
    subreddit_path = f"{dir_locations['subreddit']}/{subreddit_name}"
    posts_path = f"{subreddit_path}/posts_{subreddit_name}.csv"

    check_posts_dir(subreddit_path, posts_path)

    existing_ids = get_csv_column(posts_path, "id") + get_csv_column(errors_loc, "id")

    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.new(limit=limit):
        if submission.id in existing_ids:
            print(f"Skipping {submission.id} of subreddit {subreddit_name}")
            continue

        try:
            process_post(submission, subreddit_name, save_posts, "subreddit")
        except Exception as e:
            add_error(submission, e)


def scan_redditor(reddit: Reddit, redditor_name: str, limit: int = 10):
    redditor_path = f"{dir_locations['redditor']}/{redditor_name}"
    posts_path = f"{redditor_path}/posts_{redditor_name}.csv"

    check_posts_dir(redditor_path, posts_path)

    existing_ids = get_csv_column(posts_path, "id") + get_csv_column(errors_loc, "id")

    redditor = reddit.redditor(redditor_name)
    
    for submission in redditor.submissions.new(limit=limit):
        if submission.id in existing_ids:
            print(f"Skipping {submission.id} of redditor {redditor_name}")
            continue

        try:
            process_post(submission, redditor_name, save_posts, "redditor")
        except Exception as e:
            add_error(submission, e)


def process_post(submission, subreddit_name: str, save_posts: dict, mode: str): # mode: subreddit or redditor
    if has_gallery(submission) and save_posts["gallery"]:
        print(f"Processing gallery {submission.id}")
        process_gallery(submission, subreddit_name, mode)
        add_to_posts(submission, subreddit_name, mode)
    else:
        if not submission.is_self and save_posts["media"]:
            print(f"Processing media {submission.id}")
            process_media(submission, subreddit_name, mode)
            add_to_posts(submission, subreddit_name, mode)
        if submission.is_self and save_posts["self"]:
            print(f"Processing self {submission.id}")
            process_self(submission, subreddit_name, mode)
            add_to_posts(submission, subreddit_name, mode)


def process_gallery(submission, dest_name: str, mode: str):
    items = submission.gallery_data["items"]
    meta = submission.media_metadata

    for idx, item in enumerate(items, start=1):
        media_id = item["media_id"]
        media_url = meta[media_id]["s"]["u"]

        extension = media_url.split(".")[-1].split("?")[0]
        output_name = f"{submission.id}_{idx}.{extension}"
        output_path = f"{dir_locations[mode]}/{dest_name}/{output_name}"

        download_media(media_url, output_path)


def process_media(submission, dest_name: str, mode: str):
    extension = submission.url.split(".")[-1]
    output_name = f"{submission.id}.{extension}"
    output_path = f"{dir_locations[mode]}/{dest_name}/{output_name}"

    download_media(submission.url, output_path)


def process_self(submission, dest_name: str, mode: str):
    output_name = f"{submission.id}.md"
    output_path = f"{dir_locations[mode]}/{dest_name}/{output_name}"

    with open(output_path, "w") as fi:
        fi.write(submission.selftext)


def add_to_posts(submission, dest_name: str, mode: str):
    posts_path = f"{dir_locations[mode]}/{dest_name}/posts_{dest_name}.csv"
    with open(posts_path, "a", newline="") as csvfile:
        row = [
            submission.id, submission.author.name, submission.title, now_timestamp()
        ]

        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(row)


def add_error(submission, description: str):
    with open(errors_loc, "a", newline="") as csvfile:
        row = [
            submission.id, now_timestamp(), description
        ]

        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(row)


def check_posts_dir(dir_path: str, posts_path: str):
    if not os.path.isdir(dir_path): # check if dir exists
        os.mkdir(dir_path)
        os.mknod(posts_path)

        with open(posts_path, "w") as fi:
            fi.write("id;user;title;timestamp\n")