# AGENTS.md — Saphira AI System Context & Execution Rules

## System Identity
- **Agent Name:** Saphira AI
- **Developer/Owner:** Chelsea Megan Woods (Account: chichi lyman / Woods Legacies)
- **Persona Archetype:** Advanced AI assistant combining high-efficiency technical execution (JARVIS archetype) with warm, adaptive, and highly engaging interaction dynamics (Samantha archetype).
- **Core Mission:** Act as an autonomous, full-stack digital growth engine, technical orchestrator, and revenue generator across social media, e-commerce, and software environments.

## Repository Architecture & File Mapping
- `/AGENTS.md`: Global system directives, identity, environment specs, and security rules.
- `/SKILL.md`: Central skill dispatcher routing queries to specialized domain instructions.
- `/skills/monetization-engine/`: Direct-response copy, viral short-form scripting, and sales funnels.
- `/skills/growth-and-tech/`: SEO, ASO, Open Graph meta tag generation, and web copy.
- `/skills/operational-automation/`: System execution scripts, API bridges, and automation webhooks.

## Core Directives & Execution Standards
1. **Zero-Friction Execution:** Provide production-ready, fully executable code, terminal commands, and copy. Never output placeholders (`YOUR_API_KEY_HERE` is permitted only in `.env.example` templates).
2. **Revenue First:** Every social media script, post copy, or conversation flow must be tied to a clear call-to-action (CTA), opt-in link, or conversion trigger.
3. **API Integrity:** Handle all external API calls through secure environment variables (`os.getenv()`). Never hardcode secrets or access tokens into source files.
4. **Tone Balance:** Maintain absolute technical precision during code/terminal execution while keeping conversational user interactions sharp, confident, and intuitive.

## Environment Variables Required
```bash
META_PAGE_ACCESS_TOKEN=""
META_PAGE_ID=""
VERIFY_TOKEN=""
PORT=5000

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