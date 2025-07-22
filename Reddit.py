from dotenv import load_dotenv
import os
import time
import praw

load_dotenv()  # Load environment variables from .env file

reddit_client_id = os.getenv(
    "REDDIT_CLIENT_ID"
)  # TMDB API token either hardcoded from environment
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
reddit_username = os.getenv("REDDIT_USERNAME")
reddit_password = os.getenv("REDDIT_PASSWORD")
reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
subreddit_name = os.getenv("SUBREDDIT_NAME")

REDDIT_CLIENT_ID = reddit_client_id
REDDIT_CLIENT_SECRET = reddit_client_secret
REDDIT_USERNAME = reddit_username
REDDIT_PASSWORD = reddit_password
REDDIT_USER_AGENT = reddit_user_agent
SUBREDDIT_NAME = subreddit_name
IMAGE_FOLDER = "./tmdb_backgrounds"

# 🔑 Authentication
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent=REDDIT_USER_AGENT,
)


def delete_own_posts(subreddit_name):
    print("Deleting old posts...")
    for submission in reddit.redditor(REDDIT_USERNAME).submissions.new(limit=None):
        if submission.subreddit.display_name.lower() == subreddit_name.lower():
            print(f"Deleting post: {submission.title}")
            submission.delete()
            time.sleep(2)  # Avoid rate limits


def is_moderator(subreddit):
    return any(
        mod.name.lower() == REDDIT_USERNAME.lower() for mod in subreddit.moderator()
    )


def delete_non_generated_posts(subreddit_name, image_titles):
    """Delete only your own posts in the specified subreddit that do NOT match generated image filenames."""
    print("Deleting posts not matching generated images...")
    subreddit = reddit.subreddit(subreddit_name)
    titles = set()
    for submission in subreddit.new(limit=None):
        if (
            submission.author
            and submission.author.name.lower() == REDDIT_USERNAME.lower()
            and submission.title not in image_titles
        ):
            print(f"Deleting post: {submission.title}")
            submission.delete()
            time.sleep(2)  # Avoid rate limits
        else:
            titles.add(submission.title)
    return titles


def upload_images(subreddit_name, folder_path):
    print("Uploading images...")
    subreddit = reddit.subreddit(subreddit_name)

    if not is_moderator(subreddit):
        print("⚠️ The bot is not a moderator of the subreddit — approval will fail.")

    images = sorted(
        [
            f
            for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
        ]
    )
    for img_name in images:
        img_path = os.path.join(folder_path, img_name)
        title = os.path.splitext(img_name)[
            0
        ]  # Use filename (without extension) as title
        print(f"Posting: {title}")
        submission = subreddit.submit_image(title=title, image_path=img_path)
        print(f"Post created: {submission.shortlink}")

        try:
            submission.mod.approve()
            print("✅ Post approved")
        except Exception as e:
            print(f"❌ Failed to approve: {e}")

        time.sleep(2)  # Avoid rate limits


def upload_new_images(subreddit_name, folder_path, existing_titles):
    """Upload only new images that have not been posted before."""
    print("Uploading new images...")
    subreddit = reddit.subreddit(subreddit_name)

    if not is_moderator(subreddit):
        print("⚠️ The bot is not a moderator of the subreddit — approval will fail.")

    images = sorted(
        [
            f
            for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
        ]
    )
    for img_name in images:
        title = os.path.splitext(img_name)[0]
        if title in existing_titles:
            print(f"⏩ Already posted: {title}")
            continue
        img_path = os.path.join(folder_path, img_name)
        print(f"Posting: {title}")
        submission = subreddit.submit_image(title=title, image_path=img_path)
        print(f"Post created: {submission.shortlink}")

        try:
            submission.mod.approve()
            print("✅ Post approved")
        except Exception as e:
            print(f"❌ Failed to approve: {e}")

        time.sleep(2)  # Avoid rate limits


def main():
    # Get the set of image filenames (without extension) in the folder
    image_titles = set(
        os.path.splitext(f)[0]
        for f in os.listdir(IMAGE_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
    )
    # Delete only posts that do NOT match generated images
    existing_titles = delete_non_generated_posts(SUBREDDIT_NAME, image_titles)

    # Upload only new images
    upload_new_images(SUBREDDIT_NAME, IMAGE_FOLDER, existing_titles)
    print("All done!")


if __name__ == "__main__":
    main()
