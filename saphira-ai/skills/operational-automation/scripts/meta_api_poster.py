
---

### 2. Automated Meta Publishing Script (`meta_api_poster.py`)

Save this file as `skills/operational-automation/scripts/meta_api_poster.py`. It uses the **Meta Graph API** to publish text, image, or video posts directly to your Facebook Business Page.

```python
import os
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("META_PAGE_ID")
GRAPH_API_URL = "https://graph.facebook.com/v19.0"

def publish_text_post(message):
    """Publishes a standard text/link post to the Facebook Business Page."""
    url = f"{GRAPH_API_URL}/{PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

def publish_image_post(message, image_url):
    """Publishes an image post with a caption to the Facebook Business Page."""
    url = f"{GRAPH_API_URL}/{PAGE_ID}/photos"
    payload = {
        "caption": message,
        "url": image_url,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

def publish_video_post(title, description, video_url):
    """Publishes a video or short Reel to the Facebook Business Page."""
    url = f"{GRAPH_API_URL}/{PAGE_ID}/videos"
    payload = {
        "title": title,
        "description": description,
        "file_url": video_url,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Saphira AI - Meta Graph API Auto-Poster")
    parser.add_argument("--type", choices=["text", "image", "video"], required=True, help="Type of post to publish")
    parser.add_argument("--message", required=True, help="Post caption or message body")
    parser.add_argument("--media-url", help="URL of the image or video to publish")
    parser.add_argument("--title", help="Title for video posts")

    args = parser.parse_args()

    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        print(" Error: META_PAGE_ACCESS_TOKEN or META_PAGE_ID is not set in environment.")
        exit(1)

    print(f" Executing Meta publication task via Saphira Engine...")

    if args.type == "text":
        result = publish_text_post(args.message)
    elif args.type == "image":
        if not args.media_url:
            print(" Error: --media-url is required for image posts.")
            exit(1)
        result = publish_image_post(args.message, args.media_url)
    elif args.type == "video":
        if not args.media_url:
            print(" Error: --media-url is required for video posts.")
            exit(1)
        result = publish_video_post(args.title or "New Video", args.message, args.media_url)

    if "id" in result:
        print(f" Post published successfully! Post ID: {result['id']}")
    else:
        print(f" Failed to publish post. Response: {result}")