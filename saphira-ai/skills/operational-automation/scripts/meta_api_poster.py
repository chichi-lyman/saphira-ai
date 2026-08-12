"""
Automated Meta (Facebook) publishing helper using the Graph API.

Publishes text, image, or video posts to a Business Page.
Requires META_PAGE_ACCESS_TOKEN and META_PAGE_ID in the environment.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
PAGE_ID = os.getenv("META_PAGE_ID", "")
GRAPH_API_URL = "https://graph.facebook.com/v19.0"


def post_text(message: str) -> dict:
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        raise RuntimeError("META_PAGE_ACCESS_TOKEN and META_PAGE_ID must be set")
    url = f"{GRAPH_API_URL}/{PAGE_ID}/feed"
    resp = requests.post(
        url,
        data={"message": message, "access_token": PAGE_ACCESS_TOKEN},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def post_photo(message: str, image_url: str) -> dict:
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        raise RuntimeError("META_PAGE_ACCESS_TOKEN and META_PAGE_ID must be set")
    url = f"{GRAPH_API_URL}/{PAGE_ID}/photos"
    resp = requests.post(
        url,
        data={
            "url": image_url,
            "caption": message,
            "access_token": PAGE_ACCESS_TOKEN,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Post to Meta/Facebook Page")
    parser.add_argument("--message", required=True, help="Post text / caption")
    parser.add_argument("--image-url", default="", help="Optional public image URL")
    args = parser.parse_args(argv)

    try:
        if args.image_url:
            result = post_photo(args.message, args.image_url)
        else:
            result = post_text(args.message)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
