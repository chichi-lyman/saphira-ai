# Saphira Revenue Workspace

Generated revenue artifacts belong in this directory at runtime.

Expected Phase 1 outputs:

- `tampa_roofing_approval_queue.csv`
- `tampa_roofing_approval_summary.md`

Do not commit customer credentials, private contact data, or secrets. The approval queue defaults to `PENDING_REVIEW`; Saphira does not send external outreach automatically.

Commerce OS foundation (governance, audit, state machine, Stripe verification) lives under `src/commerce/`. See `docs/COMMERCE_OS.md`.
