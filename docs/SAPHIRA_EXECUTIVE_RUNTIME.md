# Saphira Executive Runtime

Saphira is the single conversational assistant. Specialized agents operate as quiet background workers.

## Runtime flow

```text
User -> Saphira -> Planner -> Agent Registry -> Workers -> Tools -> QA -> Memory -> Saphira
```

## Design rules

1. Users never select or manage individual agents for routine work.
2. Every meaningful request becomes a durable `Task`.
3. Planning and routing are capability-based, not personality-based.
4. Workers execute behind Saphira and report structured results.
5. Verification occurs before Saphira claims completion.
6. Low-risk reversible work may run autonomously.
7. External, financial, destructive, or irreversible actions require approval.
8. Conversation memory and operational task memory are separate concerns.
9. Existing legacy orchestrators remain available during migration; the new executive runtime is the canonical path for new features.

## Initial capabilities

- reasoning
- research
- development
- content
- commerce
- communications
- quality assurance

## Migration strategy

The runtime is additive. Existing agents and integrations should be adapted behind the worker contract instead of duplicated. Once an existing capability is migrated and tested, its legacy direct entrypoint can be deprecated.
