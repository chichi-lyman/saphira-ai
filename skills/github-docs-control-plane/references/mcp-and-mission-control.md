# MCP and mission control reference

Use this when the user wants Saphira to read the repository: issues, pull requests, file trees, and control-plane docs. The goal is a reviewed draft, not an unattended merge.

## Authority ladder

| Action | Default |
|---|---|
| Read a file, issue, PR, or tree | ALLOW |
| Comment a summary the user asked for | REQUIRE_APPROVAL |
| Open a pull request | REQUIRE_APPROVAL |
| Push a commit to a feature branch the user named | REQUIRE_APPROVAL |
| Merge, force-push, delete a branch, deploy | DENY unless the user says so in this turn |

## Tool map

Document only tools the connected runtime actually exposes. A typical GitHub MCP surface:

| Intent | Tool shape | Notes |
|---|---|---|
| Who am I | get authenticated user | Confirm the account before any write |
| List the tree | get repository tree | Verify a path before a doc tells agents to import it |
| Find a symbol | search code | Scope with `repo:owner/name` |
| Read an issue or PR | get / search issues and pull requests | Quote the number in the summary |
| Write files | push files, or create-or-update contents | One commit, feature branch, message states the rule that changed |
| Open a PR | create pull request | Body lists files, the rule, and the still-manual GitHub setting |

If a tool is not in the live tool list, say so. Do not invent an MCP server name.

## Mission-control prompt

Give this to a session that should treat the repo as memory. Replace the path list with files that exist.

```
Operate as Saphira, mission control for this architecture.
Read AGENTS.md, .github/copilot-instructions.md, docs/core/governance.md,
and the capability catalog. Treat those as operational memory.
Pipeline order is fixed:
Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero.
Do not reorder it. Do not merge. Draft the change and stop for review.
```

## Drafting a pull request

1. Read the control file you will change.
2. Patch it. Do not regenerate unrelated docs.
3. Commit on a branch named `docs/<short-topic>`.
4. Open a pull request whose body uses:

```markdown
## Rule that changed
<one sentence>

## Files
- path — created or patched

## Still manual
- <GitHub setting, or "none">

## Pipeline
No change to pipeline order.
```

5. Stop. Review is the next step. Merging is a separate instruction.

## Self-heal, bounded

"Self-heal" in this skill means: a check failed, the log names a file, you patch that file, you re-run the check.

It does not mean: scanning the repo for things to rewrite, committing to the default branch, or "fixing" a red CI job you have not read.

## Compliance check before a docs PR

- Pipeline line matches governance exactly.
- No secret-shaped string in the diff.
- Every new path mentioned in the doc exists after this change.
- User-facing PR text does not list internal worker names beyond the pipeline line already public in `AGENTS.md`.
