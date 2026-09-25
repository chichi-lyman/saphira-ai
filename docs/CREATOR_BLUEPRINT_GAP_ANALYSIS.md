# Creator platform blueprint vs Saphira AI

Mapped against the build blueprint (money → community → discovery).

## Already strong

- AI/ML services and multi-agent runtime (core differentiator)
- Content distribution connectors (FeedHive / Publer where configured)
- Engineering foundation (monorepo, CI, tests)
- Governed commerce kernel (policy, audit, Stripe verify)
- Freemium / pricing thinking in pitch materials

## Gaps ranked

| Gap | Severity | Wedge response |
|-----|----------|----------------|
| Payments / payouts / fee engine | Critical | Stripe Checkout + webhook + order ledger (single merchant dogfood) |
| Multi-tenant served product | Critical | Thin creator API only; full studio UI still out of scope |
| User auth (creator/audience) | Critical | Use Stripe customer email + existing tenant ids; full auth later |
| Postgres content/audience store | High | Optional DATABASE_URL for orders/tenants |
| Subscriptions, tips, PPV, products | High | Catalog + checkout for book/course/sub/kit |
| Community | Medium | Phase 2 |
| Media pipeline | Medium | Outsource |
| Mobile | Later | — |

## Strategic choice

Do **not** build a full two-sided creator network solo with no budget.  
Do **dogfood** commerce on Chelsea’s own funnel until payouts are boring and reliable. Then open Connect.

See [CREATOR_PLATFORM_WEDGE.md](./CREATOR_PLATFORM_WEDGE.md).
