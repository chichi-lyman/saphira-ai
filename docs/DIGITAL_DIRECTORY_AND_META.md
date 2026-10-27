# Digital Directory & Meta Graph Integration

© 2026 Chelsea Megan Woods · Nova Umbrella / Woods AI Studio

This document describes how Saphira is connected to the master digital directory and what the Meta Graph API surface enables for the Facebook Page (and linked Instagram).

## Master Directory

Canonical account map lives at:

```
config/digital_directory.yaml
```

It contains:

- Social profiles (X, TikTok, Instagram, Facebook, YouTube primary + media, LinkedIn)
- Link hubs & wishlists (youpay.bio, Beacons, Throne, Amazon)
- Payment / P2P handles (Cash App, PayPal, Chime)
- Developer hubs (GitHub profile + saphira-ai + Nova_Umbrella)

Saphira uses this file as the single source of truth for identity when generating content, drafting replies, or routing commerce/support questions.

## Facebook / Meta Graph API (already wired)

Connector: `src/connectors/facebook.py`

### 1. Automated Content Creation & Publishing
- `post(message, link=None, scheduled_publish_time=None)` — text/status or link posts, optional scheduling
- `upload_photo(image_url, caption=None)` — stream promotional visuals into the feed
- `schedule_post(...)` — convenience wrapper
- GitHub Actions workflow `.github/workflows/social-media-post.yml` can trigger posts on timers, commits, or pipeline events once secrets are set.

### 2. Audience Engagement & Moderation
- `get_comments(post_id)` / `reply_to_comment(comment_id, message)` — conversational replies in brand voice
- `hide_comment(comment_id, hide=True)` — triage spam/toxic input
- `get_conversations` + `send_messenger_message` — basic Messenger support (requires `pages_messaging` permission)

### 3. Analytics & Growth Optimization
- `get_page_insights` / `get_post_insights` — reach, impressions, reactions, follower growth
- `list_recent_posts` — feed the optimization loop so Saphira can prefer high-performing formats, hooks, and hashtags

## Required Secrets / Env Vars

Add to production `.env` / GitHub Actions secrets / Vercel:

```
FACEBOOK_ACCESS_TOKEN=<long-lived Page access token>
FACEBOOK_PAGE_ID=<numeric Page ID>
FACEBOOK_GRAPH_VERSION=v19.0   # optional

INSTAGRAM_ACCESS_TOKEN=...    # often same Meta app
INSTAGRAM_USER_ID=...

# Existing social keys already referenced by the workflow
TWITTER_API_KEY / SECRET / ACCESS_TOKEN / ACCESS_SECRET
TIKTOK_CLIENT_KEY / SECRET / ACCESS_TOKEN
# etc.
```

### How to obtain a long-lived Page token (summary)
1. Create or use a Meta Business app at developers.facebook.com
2. Add Facebook Login + required products
3. Request scopes: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `pages_manage_engagement`, `pages_messaging` (as needed), plus Instagram scopes if linking IG
4. Generate short-lived user token → exchange for long-lived user token → exchange for long-lived Page token
5. Store only the Page token in Saphira secrets

## Governance

All publish, reply, and DM actions remain behind Nova Reign communications policy gates. Saphira never autonomously posts or messages without the configured approval path.

## Next practical steps for you
1. Populate `FACEBOOK_ACCESS_TOKEN` + `FACEBOOK_PAGE_ID` (and Instagram pair) in the deployment environment.
2. Confirm the Facebook Page is the one owned by the `xx.Its.chichi.xx` profile / business asset.
3. Optionally extend the hourly GitHub Actions workflow to also call the new Facebook methods.
4. Tell Saphira in chat: “Post this to Facebook” or “Pull page insights for the last 7 days” — she will route through the connector once credentials are live.
