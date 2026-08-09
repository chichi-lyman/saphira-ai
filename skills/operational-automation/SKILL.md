---
name: saphira-operational-automation
description: Automates direct execution tasks including API posting, DM webhook replies, video rendering, and trend scraping via terminal scripts.
when_to_use: |
  - User asks Saphira to automatically post content, process messages, or render short-form video
  - User requests live trend analysis or competitor scraping
---

# Saphira AI: Operational Automation Engine

## 1. Automated Social Media Publishing
* **Directive:** Execute `python3 skills/operational-automation/scripts/meta_api_poster.py` to publish or schedule approved captions and media assets directly to Meta/TikTok accounts.

## 2. Inbound DM & Comment Webhook Execution
* **Directive:** Process payload triggers from social media comments/DMs and run `dm_webhook_handler.py` to deliver automated sales links and qualify leads.

## 3. Video Rendering Pipeline
* **Directive:** Take written short-form scripts and pass the parameters to `video_renderer.py` to auto-generate video clips with subtitled overlays and voiceovers.

## 4. Live Trend Scraper
* **Directive:** Execute `trend_scraper.py` on a weekly schedule to pull top-performing industry hooks, viral audio tags, and search keywords for immediate script generation.
