# Learning ledger

Copyright © 2026 Chelsea Megan Woods

Append-only. Newest entry first. A row here is a sourced note, not a change to `AGENTS.md`.

## 2026-10-22 — How this repo stays online

- Claim: GitHub Copilot loads `.github/copilot-instructions.md` as repository-wide custom instructions, and it also loads `AGENTS.md` from anywhere in the tree (the nearest file wins). On github.com/copilot those instructions apply when this repository is attached to the chat, and the instructions file is added as a reference on the answer. There is no separate "enable internet" switch. An agent that already has web search uses it, then writes the finding here so the next session does not look up the same fact.
- Source: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- Affects: `.github/copilot-instructions.md`, `AGENTS.md`, this ledger
- Promoted to a hard rule: no

## 2026-10-22 — Where live search actually runs

- Claim: This checkout has no module named as a web-search client. A code search for `web_search`, `tavily`, and `duckduckgo` on 2026-10-22 returned no matches. DeepSearch is already specified as multi-step internet and X search in `docs/GROK_CAPABILITIES.md`. Use that when a survey was asked for. Do not invent a second search client to satisfy this ledger.
- Source: GitHub code search, `repo:chichi-lyman/saphira-ai web_search OR tavily OR duckduckgo`, 2026-10-22, 0 results. Capability statement in `docs/GROK_CAPABILITIES.md`.
- Affects: agents about to add a search dependency
- Promoted to a hard rule: no
