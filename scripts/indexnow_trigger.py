# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-frontmatter>=1.0.0",
# ]
# ///
import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import frontmatter

# Configuration
INDEXNOW_KEY = os.getenv("INDEXNOW_KEY")
SITE_URL = os.getenv("SITE_URL", "https://paulushcgcj.github.io").rstrip("/")
TRIGGER_MODE = os.getenv("TRIGGER_MODE", "push")  # 'push' or 'cron'
MODIFIED_FILES = os.getenv("MODIFIED_FILES", "").split()

# Vancouver timezone (handles BC Daylight Saving Time automatically)
VANCOUVER_TZ = ZoneInfo("America/Vancouver")

# Narrow window for cron to catch scheduled posts without duplicates
CRON_WINDOW_MINUTES = 20


def get_datetime_safe(post_date) -> datetime:
    """Ensure we have a timezone-aware datetime object."""
    if isinstance(post_date, datetime):
        # If naive, assume it's meant to be in Vancouver time (common in Jekyll)
        if post_date.tzinfo is None:
            return post_date.replace(tzinfo=VANCOUVER_TZ)
        return post_date

    date_str = str(post_date).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=VANCOUVER_TZ)
        return dt
    except ValueError:
        # Fallback: parse YYYY-MM-DD and assume midnight Vancouver time
        dt = datetime.strptime(date_str.split()[0], "%Y-%m-%d").replace(
            tzinfo=VANCOUVER_TZ
        )
        return dt


def get_absolute_url(post_path: str) -> str:
    """Extract permalink from frontmatter and make it absolute."""
    post = frontmatter.load(post_path)
    metadata = post.metadata

    permalink = metadata.get("permalink")

    if permalink:
        if permalink.startswith("http"):
            return permalink
        return f"{SITE_URL}{permalink}"

    # Fallback
    slug = post.get("slug") or os.path.basename(post_path).replace(".md", "")[11:]
    return f"{SITE_URL}/{slug}/"


def main():
    if not INDEXNOW_KEY:
        print("❌ INDEXNOW_KEY environment variable is not set.")
        sys.exit(1)

    posts_dir = "_posts"
    if not os.path.exists(posts_dir):
        print(f"⚠️ Directory '{posts_dir}' not found.")
        sys.exit(0)

    urls_to_submit = []
    now_vancouver = datetime.now(VANCOUVER_TZ)
    now_utc = datetime.now(timezone.utc)

    modified_set = (
        set(MODIFIED_FILES)
        if MODIFIED_FILES
        else set(
            os.path.join("_posts", f)
            for f in os.listdir("_posts")
            if f.endswith(".markdown")
        )
    )

    # Loop through the whole _posts folder
    for filename in os.listdir(posts_dir):
        if not filename.endswith(".markdown"):
            print(f"⚠️ Skipping non-markdown file: {filename}")
            continue

        file_path = os.path.join(posts_dir, filename)
        print(f"🔍 Processing {file_path}...")

        try:
            post = frontmatter.load(file_path)
            metadata = post.metadata
            markdown = post.content
        except Exception as e:
            print(f"⚠️ Failed to parse {file_path}: {e}")
            continue

        post = metadata
        post["_content"] = markdown

        # 1. Validate: Is the post published? (date <= now)
        post_date = post.get("date")
        update_date = post.get("lastupdated") or post.get("last_modified_at")
        if not post_date:
            print(f"⚠️ No 'date' found in frontmatter for {file_path}. Skipping.")
            continue  # Skip undated posts

        dt_post = get_datetime_safe(post_date)
        dt_update = get_datetime_safe(update_date) if update_date else None

        # Convert to UTC for a safe "is it published yet?" check
        if dt_post > now_utc:
            print(
                f"⚠️ Post {file_path} is scheduled for the future ({dt_post}). Skipping."
            )
            continue  # Skip future-dated posts

        # 2. Decide whether to submit based on trigger mode
        should_submit = False

        if TRIGGER_MODE == "push":
            print(f"ℹ️ Push mode: Checking if {file_path} is in modified files.")
            # Push mode: Rely on git diff. If it's modified and published, submit it.
            if file_path in modified_set:
                print(
                    f"✅ {file_path} is modified and published. Queuing for submission."
                )
                should_submit = True

        elif TRIGGER_MODE == "cron":
            # Cron mode: Use 'lastupdated' if available, otherwise 'date'
            post_lastupdated = post.get("lastupdated")
            if post_lastupdated:
                dt_post = get_datetime_safe(post_lastupdated)
                print(
                    f"ℹ️ Using lastupdated for {os.path.basename(file_path)}: {dt_post}"
                )
            else:
                dt_post = get_datetime_safe(post.get("date"))
                print(f"ℹ️ Using date for {os.path.basename(file_path)}: {dt_post}")

            dt_post_vancouver = dt_post.astimezone(VANCOUVER_TZ)
            time_since_publish = now_vancouver - dt_post_vancouver

            print(f"📅 Vancouver now: {now_vancouver}")
            print(f"📅 Post published: {dt_post_vancouver}")
            print(f"⏱️ Time since publish: {time_since_publish}")
            print(f"⏱️ CRON_WINDOW_MINUTES: {CRON_WINDOW_MINUTES}")

            if (
                timedelta(0)
                <= time_since_publish
                <= timedelta(minutes=CRON_WINDOW_MINUTES)
            ):
                should_submit = True
                print(f"✅ Within cron window")
            else:
                print(f"❌ Outside cron window (0 to {CRON_WINDOW_MINUTES} minutes)")

        if should_submit:
            url = get_absolute_url(file_path)
            urls_to_submit.append(url)
            print(f"✅ Queued ({TRIGGER_MODE}): {url}")

    if not urls_to_submit:
        print("ℹ️ No valid, recently updated/published URLs to submit.")
        sys.exit(0)

    # Deduplicate URLs
    urls_to_submit = list(set(urls_to_submit))

    payload = {
        "host": "paulushcgcj.github.io",
        "key": INDEXNOW_KEY,
        "urlList": urls_to_submit,
    }

    req = urllib.request.Request(
        "https://www.bing.com/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(
                    f"🎉 Successfully submitted {len(urls_to_submit)} URL(s) to IndexNow."
                )
            else:
                print(
                    f"⚠️ IndexNow returned status {response.status}: {response.read().decode()}"
                )
                sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Failed to reach IndexNow endpoint: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
