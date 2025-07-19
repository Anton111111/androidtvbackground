import os
import time
import praw

reddit_client_id = locals().get('token', os.getenv('REDDIT_CLIENT_ID'))  # TMDB API token either hardcoded from environment
reddit_client_secret = locals().get('token', os.getenv('REDDIT_CLIENT_SECRET'))
reddit_username = locals().get('token', os.getenv('REDDIT_USERNAME'))
reddit_password = locals().get('token', os.getenv('REDDIT_PASSWORD'))
reddit_user_agent = locals().get('token', os.getenv('REDDIT_USER_AGENT'))
subreddit_name = locals().get('token', os.getenv('SUBREDDIT_NAME'))

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
    user_agent=REDDIT_USER_AGENT
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
        mod.name.lower() == REDDIT_USERNAME.lower()
        for mod in subreddit.moderator()
    )

def upload_images(subreddit_name, folder_path):
    print("Uploading images...")
    subreddit = reddit.subreddit(subreddit_name)

    if not is_moderator(subreddit):
        print("⚠️ The bot is not a moderator of the subreddit — approval will fail.")

    images = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    ])
    for img_name in images:
        img_path = os.path.join(folder_path, img_name)
        title = os.path.splitext(img_name)[0]  # Use filename (without extension) as title
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
    delete_own_posts(SUBREDDIT_NAME)
    upload_images(SUBREDDIT_NAME, IMAGE_FOLDER)
    print("All done!")

if __name__ == "__main__":
    main()
