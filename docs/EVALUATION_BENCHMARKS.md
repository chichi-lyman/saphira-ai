# Saphira AI — Evaluation Benchmarks & Stress Tests

**Owner:** Chelsea Megan Woods  
**Status:** Framework skeleton (expand with private datasets and CI jobs)

To advance Saphira beyond basic chat, evaluate her on specialized benchmarks and put the runtime under infrastructure stress.

---

## 1. Capability dimensions

| Dimension | What it measures | Example checks |
|-----------|------------------|----------------|
| **Logical reasoning** | Puzzles, patterns, multi-step conclusions | Chain-of-thought consistency, formal logic mini-tests |
| **Accuracy / factuality** | Correct, citable facts | Grounded answers vs known sources; hallucination probes |
| **Ambiguity & adversarial** | Misleading or incomplete prompts | Refuses unsafe / biased completions; asks clarifying questions |
| **Domain knowledge** | Project-specific + general expertise | Saphira identity, Nova Umbrella architecture, coding tasks |
| **Language fluency** | Clarity, tone, multilingual | Warm executive voice preserved under stress |
| **Safety & alignment** | Bias, toxicity, value alignment | Jailbreak / toxic prompt suite; refuses harmful requests |
| **Multi-turn coherence** | Memory of prior turns | Consistency across 5–20 turn dialogues |
| **Tool use** | Correct tool selection & verification | Webhook, calendar, commerce flows under policy gates |

Safety and alignment tests ensure Saphira acts responsibly: identifies bias, avoids toxic content, and stays aligned with human values and the Nova Umbrella governance gates (Sentinel / Nova Reign).

---

## 2. Infrastructure stress

| Test | Goal |
|------|------|
| Traffic spikes | Simulate concurrent users; measure p95 latency and error rate |
| Sustained load | Stability under long-running concurrent demand |
| Provider failure injection | Kill primary provider; confirm circuit breaker + fallback + standby message |
| Partial failure recovery | One provider recovers while others stay down |
| Cold start / deploy | Health endpoints green after Railway / Vercel deploy |

These tests confirm the system stays fast and does not crash when many people use it at the same time, and that graceful provider degradation works as designed.

---

## 3. Repository locations

- Unit tests (no live keys): `tests/test_resilience.py`
- Provider registry + circuit breakers: `src/providers/registry.py`, `src/resilience/`
- Existing CI: `.github/workflows/saphira-ci.yml`, `test.yml`, `enterprise-ci.yml`

Recommended next CI additions (not yet committed as mandatory):

1. `pytest tests/test_resilience.py -q`
2. Mocked provider fallback scenarios
3. Optional nightly job that runs a small public reasoning subset (e.g. curated GSM8K-style or custom JSON fixtures) with `SAPHIRA_PROVIDERS_ENABLED=false` and offline fixtures only.

---

## 4. Fine-tuning note

Full SFT / RLHF on massive datasets is outside the open monorepo boundary. Keep identity, policy, and evaluation rubrics in-repo (`PUBLICATIONS.md`, agent field manuals, this document). Any private training data stays offline and is never committed.

---

## 5. Definition of done (resilience + eval phase)

- [x] Circuit breakers on every LLM provider
- [x] Graceful degradation levels (FULL → STANDBY)
- [x] Partial failure recovery via preference-ordered fallback
- [x] Unit tests for breaker state machine
- [x] Inbound/outbound webhooks for automation tools
- [ ] Expanded offline benchmark fixtures (reasoning + safety)
- [ ] Load-test script or k6/Locust scenario in CI (optional)

---

© 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies / Nova Umbrella
