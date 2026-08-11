# Saphira TikTok Autopilot

Saphira now includes a server-side TikTok Content Posting API adapter for Chelsea's `@chelseameganwoods` content pipeline.

## Capabilities

- TikTok OAuth v2 authorization with server-side state stored in Redis.
- `video.publish` authorization for Direct Post.
- Creator-info lookup before publishing.
- Direct video posting from a verified/allowed video URL using `PULL_FROM_URL`.
- Publish-status polling using `publish_id`.
- Automatic access-token refresh using TikTok refresh tokens.
- Redis persistence for TikTok OAuth tokens.
- Server-to-server automation-key protection for publish/status/creator endpoints.

## Required environment variables

```text
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
TIKTOK_REDIRECT_URI=https://YOUR_BACKEND_DOMAIN/api/tiktok/oauth/callback
REDIS_URL=redis://...
SAPHIRA_TIKTOK_AUTOMATION_KEY=
SAPHIRA_WEB_ORIGIN=https://YOUR_FRONTEND_DOMAIN
```

Never place `TIKTOK_CLIENT_SECRET`, access tokens, or refresh tokens in frontend code.

## TikTok Developer Portal

1. Register a TikTok developer app.
2. Add the Content Posting API product.
3. Enable Direct Post.
4. Configure the exact static redirect URI from `TIKTOK_REDIRECT_URI`.
5. Request/obtain approval for the `video.publish` scope.
6. Complete TikTok's audit before expecting public visibility from an audited production client. Unaudited clients are restricted to private visibility.

## API flow

1. `GET /api/tiktok/oauth/start`
2. Redirect the user to the returned TikTok authorization URL.
3. TikTok redirects to `GET /api/tiktok/oauth/callback`.
4. Saphira exchanges the one-time authorization code server-side and stores the refreshable token in Redis.
5. Saphira queries creator settings before each Direct Post.
6. `POST /api/tiktok/publish/{open_id}` submits the hosted video URL.
7. TikTok returns `publish_id`.
8. `POST /api/tiktok/status/{open_id}/{publish_id}` polls until the post reaches a terminal state.

## Video hosting requirement

The Direct Post implementation uses `PULL_FROM_URL`. The video URL therefore needs to satisfy TikTok's Content Posting API URL/domain requirements. For Saphira's production content engine, host generated videos on a verified domain or switch the adapter to TikTok's file-upload path for locally produced assets.

## Security model

OAuth tokens remain server-side. Publishing endpoints require `X-Saphira-Automation-Key`, which must be stored as a backend secret and never embedded in a public Vercel bundle.

## Important TikTok platform constraint

TikTok controls whether a developer client is audited and whether posted content can be publicly visible. Saphira can automate the approved API flow, but it cannot bypass TikTok's app review, authorization, moderation, or visibility controls.
