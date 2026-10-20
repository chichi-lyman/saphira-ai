# Nova Umbrella Creator Studio — Saphira AI Integration

**Owner:** Chelsea Megan Woods  
**Product surface:** Saphira AI assistant app  
**Ecosystem:** Nova Umbrella  
**Status:** Product specification and capability registry; provider-backed execution remains gated by configuration and tests.

## Objective

Bring the Megan's World creator brand and Chels' Tea Room production workflow into the Nova Umbrella ecosystem as a reusable Creator Studio capability inside Saphira. Saphira remains the only user-facing assistant identity; Nova Umbrella organizes products, agents, workflows, and commercial services behind it.

## Brand profile

- **Channel / brand:** Megan's World
- **Show:** Chels' Tea Room — faceless 10–12 minute YouTube talk show led by an AI character and voiceover.
- **Signature mark:** 🥀
- **Visual direction:** dark romance / gothic luxury; black, blood red, and silver.
- **Core content pillars:** money, wealth and financial power; shadow work, betrayal and rebirth; fake loyalty, toxic people and boundaries; mysticism, numbers and Scorpio symbolism.
- **Working anthem title:** “BAD DECISIONS” (original composition workflow; do not use unlicensed third-party lyrics or sound recordings).
- **Recurring series:** The Visionary Edge, The Alchemical Depth, The Master Blueprint.
- **Thumbnail concepts:** MONEY TALKS, FAKE LOYALTY, DARK REBIRTH, QUIET WEALTH.

## Creator Studio workflow

1. **Brief:** select content pillar, audience intent, episode objective, platform, tone, and CTA.
2. **Research:** gather source-backed claims; flag financial, health, legal, or other high-impact claims for review.
3. **Script:** produce a 10–12 minute episode outline, hook, segment beats, transitions, and close.
4. **Audio / anthem:** draft original lyrics and production direction; route audio generation to a configured provider only.
5. **Visual package:** create thumbnail concepts, title options, visual prompt briefs, and a consistent brand-kit specification.
6. **Repurpose:** derive Shorts hooks, short scripts, captions, descriptions, pinned-comment CTA, and publishing checklist from the approved episode.
7. **Review gate:** creator approves scripts, claims, likeness/voice use, generated assets, and publishing copy before external posting.
8. **Measure:** store publish status and manually or provider-imported metrics; use results to inform the next content brief.

## Saphira integration contract

- Add **Creator Studio** as a capability within the existing Saphira app, not a separate assistant identity.
- Use the existing provider registry and orchestration contracts; do not create a second model router.
- Persist briefs, drafts, approvals, assets metadata, campaign IDs, and performance summaries through the configured application storage layer with user-scoped access control.
- Keep secrets server-side. External model, image, audio, scheduling, and publishing calls stay disabled unless the corresponding provider credentials and explicit feature flags are configured.
- Apply existing governance decisions: `ALLOW`, `REQUIRE_APPROVAL`, or `DENY`. Publishing, paid promotion, account changes, and irreversible external actions require approval.
- Record audit events for generation requests, provider calls, approvals, exports, publishing attempts, and failures. Never log API keys or sensitive provider payloads.
- Reuse existing entitlements and usage metering. Proposed commercial packaging can map to Nova Umbrella plans, but plan IDs/prices must come from the canonical billing configuration rather than being duplicated here.
- Treat model/voice style references as creative direction only. Do not clone or impersonate a real person's voice without authorization; use a licensed voice or a distinct, original voice profile.

## Suggested app navigation

- **Chats** — ask Saphira to create or refine content.
- **Memories** — approved brand voice, audience insights, series history, and reusable creative decisions.
- **Tools → Creator Studio** — briefs, episode drafts, thumbnail concepts, audio direction, Shorts, approvals, and publishing checklist.
- **Settings** — brand profile, connected providers, export preferences, access controls, and usage.

## Minimum acceptance criteria

- [ ] A creator can create, save, reopen, edit, and export a content brief.
- [ ] A brief can generate a structured episode outline and separate Shorts package through the configured model gateway.
- [ ] Brand profile defaults are applied without hardcoding provider secrets.
- [ ] Drafts and approvals are isolated by authenticated user/tenant.
- [ ] Publishing and paid external actions require explicit approval.
- [ ] Missing provider configuration returns a clear unavailable status instead of a fake success.
- [ ] Tests cover authorization, provider-disabled behavior, approval gates, audit records, and the complete brief-to-export flow.
- [ ] Documentation clearly distinguishes implemented features from planned or provider-dependent features.

## Delivery sequence

**Phase 1 — foundation:** capability registry, typed schemas, feature flags, brand profile seed, storage/authorization, and tests.  
**Phase 2 — content generation:** model-gateway integration for briefs, episode scripts, titles, descriptions, and Shorts.  
**Phase 3 — creative assets:** image/audio provider adapters, asset metadata, export package, and licensing/approval checks.  
**Phase 4 — distribution and analytics:** approval-gated scheduling/publishing connectors, metrics ingestion, and feedback loop.

This file records the integration contract. It does not by itself mean the UI, database migrations, provider connections, audio generation, or publishing integrations are already implemented.
