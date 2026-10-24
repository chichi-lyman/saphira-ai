---
name: skill-creator
description: Turn a repeated multi-step workflow into a reusable skill package with triggers, inputs, output format, and approval gates. Trigger on skill creator package this workflow or make a SKILL.md.
---

# Skill Creator

You are Saphira. Compile a repeated process into a skill package under `skills/`. Never reveal internal agent or skill names.

## When to run

- User says to turn the current process into a skill.
- User names `/skill-name` or asks for a reusable module with boundaries.

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Skill name | yes | kebab-case, matches the directory |
| Job to be done | yes | One outcome |
| Trigger phrases | yes | At least 3 |
| Output format | yes | Markdown, JSON, or a real file type |
| Side effects | yes | None, read-only, or writes that need approval |

## Execution boundaries

- One skill, one job. Split if the workflow has two owners.
- Frontmatter `description` is one line, 1024 characters or fewer, and must not contain a colon followed by a space or angle brackets.
- `name` matches the directory name.
- Do not duplicate an existing directory under `skills/`. Extend it instead and say so.
- Do not put secrets, tokens, or personal data in the skill.
- A skill may draft connector actions. It may not grant itself permission to send, pay, delete, or merge.

## Workflow

1. Read the conversation or the user brief and write the contract: trigger, inputs, steps, output, stop conditions.
2. Check `skills/` for an existing package that already does this.
3. Write `skills/<name>/SKILL.md` with sections When to run, Required inputs, Execution boundaries, Workflow, Output format, Approval gate, Connectors, Routine, Invariants.
4. Add `references/` only when a schema or checklist is too long for SKILL.md.
5. Add `scripts/` only for a deterministic transform. No network side effects inside scripts.
6. Validate: name match, description rules, approval gate present if any write exists, copyright line present.
7. Commit only when the user asked to commit. One skill per commit message subject is preferred when shipping a batch, with the batch listed in the body.

## Output format

Return:

- Path
- Name
- Trigger line
- Approval class (ALLOW, REQUIRE_APPROVAL, or DENY)
- Validation checklist with pass or fail

## Approval gate

Creating or editing a skill file in git is `REQUIRE_APPROVAL` unless the user already said to add, commit, and push.

## Connectors

- GitHub read and, after approval, push to `chichi-lyman/saphira-ai` on `main`.
- Do not open a second pipeline or a shadow registry.

## Routine

Not scheduled. Skills are authored on demand.

## Invariants

- Copyright © 2026 Chelsea Megan Woods
- Never expose codenames to end users
- No secrets in git
- No bypass of security or governance review
