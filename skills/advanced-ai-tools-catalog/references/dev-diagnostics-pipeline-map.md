# Development & Diagnostics Skills → Saphira Pipeline Map

Maps the 15 Development & Diagnostics skills (catalog entries 1–15) onto the fixed Saphira executive pipeline and extended agents.

## Pipeline reminder

```
Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory / MCP) → Agent Zero (execution)
```

Extended specialists (Apex, Lexis, Instinct, Cipher, Scholar, Lyra) are dispatched by Nova Reign when the capability registry routes to them.

## Mapping

| # | Skill | Primary Owner(s) | Supporting | Notes |
|---|-------|------------------|------------|-------|
| 1 | **code-review-pro** | Agent Zero + Saphira surface | Agent Two (security findings) | Pre-merge review. Security issues escalate to Agent Two. |
| 2 | **test-driven-development** | Agent Zero | Nova Reign (quality gates) | Enforce tests before feature acceptance. |
| 3 | **system-debugging** | Agent Zero + NovaAethrea | Agent Two | Log / trace analysis; security anomalies to Agent Two. |
| 4 | **browser-use** | Agent Two (primary) + Aura | Agent Zero | Live browser control is high-risk; stays under Agent Two security boundary. |
| 5 | **mcp-builder** | NovaAethrea + Agent Zero | Agent Two, Nova Reign | New pipeline connections / tool adapters. Policy gates required. |
| 6 | **api-and-interface-design** | Agent Zero + NovaAethrea | Nova Reign | Structural data pathways and adapter contracts. |
| 7 | **frontend-ui-engineering** | Aura | Agent Zero | UI work lives with perception / content agent. |
| 8 | **refactor-expert** | Agent Zero | Saphira surface | Cleanup of heavy or messy code. |
| 9 | **grill-me** | Saphira + Nova Reign | — | Adversarial questioning of designs; governance flavor. |
| 10 | **grill-with-docs** | Saphira + Nova Reign | Agent Scholar (if deep docs) | Grounded challenge against official references. |
| 11 | **codebase-design** | Nova Reign + Agent Zero | Saphira | Structural layouts for new systems / agents. |
| 12 | **setup-skills** | NovaAethrea + Agent Zero | Nova Reign | Automated configuration of new skills / workflows. |
| 13 | **package-as-skill** | NovaAethrea + Agent Zero | — | Turn temporary workflows into reusable SKILL.md packages. |
| 14 | **dependency-checker** | Agent Zero | Agent Two | Conflict resolution + security scanning of deps. |
| 15 | **legacy-migrator** | Agent Zero + Cipher | Nova Reign | Modernization of older code; architecture oversight. |

## Usage guidance for Saphira

When a user request matches a Development & Diagnostics skill:

1. Route through the fixed pipeline (do not skip security or governance).
2. Prefer the Primary Owner for implementation.
3. Escalate to Agent Two for any browser, external network, secret, or auth work.
4. Register new artifacts (skills, adapters, schemas) via NovaAethrea so they become part of the capability surface.
5. Keep the user-facing voice as Saphira only.

## High-priority expansion order (recommended)

1. **mcp-builder** (already expanded)
2. **browser-use** (Agent Two controlled)
3. **code-review-pro** + **system-debugging**
4. **package-as-skill** + **setup-skills** (skill factory)
5. **dependency-checker** + **security-audit** (cross-link to Security category)
