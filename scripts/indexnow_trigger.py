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
        dt = datetime.strptime(date_str.split()[0], "%Y-%m-%d").replace(tzinfo=VANCOUVER_TZ)
        return dt

def get_absolute_url(post_path: str) -> str:
    """Extract permalink from frontmatter and make it absolute."""
    with open(post_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
        permalink = post.get("permalink")
        
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
    
    modified_set = set(MODIFIED_FILES) if MODIFIED_FILES else set()

    # Loop through the whole _posts folder
    for filename in os.listdir(posts_dir):
        if not filename.endswith(".md"):
            continue
            
        file_path = os.path.join(posts_dir, filename)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except Exception as e:
            print(f"⚠️ Failed to parse {file_path}: {e}")
            continue

        # 1. Validate: Is the post published? (date <= now)
        post_date = post.get("date")
        if not post_date:
            continue # Skip undated posts
            
        dt_post = get_datetime_safe(post_date)
        
        # Convert to UTC for a safe "is it published yet?" check
        if dt_post > now_utc:
            continue  # Skip future-dated posts

        # 2. Decide whether to submit based on trigger mode
        should_submit = False
        
        if TRIGGER_MODE == "push":
            # Push mode: Rely on git diff. If it's modified and published, submit it.
            if file_path in modified_set:
                should_submit = True
                
        elif TRIGGER_MODE == "cron":
            # Cron mode: Rely strictly on the 'date' field and a narrow time window.
            dt_post_vancouver = dt_post.astimezone(VANCOUVER_TZ)
            time_since_publish = now_vancouver - dt_post_vancouver
            
            if timedelta(0) <= time_since_publish <= timedelta(minutes=CRON_WINDOW_MINUTES):
                should_submit = True

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
        "urlList": urls_to_submit
    }
    
    req = urllib.request.Request(
        "https://www.bing.com/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"🎉 Successfully submitted {len(urls_to_submit)} URL(s) to IndexNow.")
            else:
                print(f"⚠️ IndexNow returned status {response.status}: {response.read().decode()}")
                sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Failed to reach IndexNow endpoint: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()