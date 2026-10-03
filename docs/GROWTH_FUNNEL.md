# Saphira AI — Automated High-Converting Funnel Architecture
**Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.**
**Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies**

## Funnel Flow

```
[TikTok / Reels / Ads] ──► [Saphira Live Interactive Page] ──► [Free Trial Opt-In]
                                     │                             │
                                     ▼                             ▼
                            [Stripe Tier Upgrade]        [n8n Email Onboarding]
                            (Free / $19 / $49 / $199)   (Automated Sequences)
                                     │
                                     ▼
                            [WhatsApp lead magnet 813-347-0699]
                            (10 free msgs → upgrade CTA)
```

### Top of Funnel (Awareness)
Viral short-form video hooks on TikTok, Instagram Reels, and YouTube Shorts demonstrating Saphira holding a warm conversation while live background notifications pop up.

### Middle of Funnel (Engagement)
Visitors land on the dark-mode luxury page (Woods AI Studio) to interact with Saphira's live WebGL visual avatar in real time. Link-in-bio routes to WhatsApp (`wa.me/18133470699`) as the primary lead magnet.

### Bottom of Funnel (Conversion)
Users sign up for the **Free Tier** (including WhatsApp freemium: 10 messages) to experience hands-free daily organization, triggering an automated email sequence and in-chat upgrade CTAs that guide them toward **Dangerous ($19)**, **Baddie ($49)**, and **CEO ($199)** upgrades.

## Pricing Tiers
| Tier       | Price    | Focus                                          |
|------------|----------|------------------------------------------------|
| Free       | $0       | Core conversation + limited agents (10 WhatsApp msgs) |
| Dangerous  | $19/mo   | Full agent suite + memory                      |
| Baddie     | $49/mo   | Priority + advanced automation                 |
| CEO        | $199/mo  | Unlimited + 1:1 onboarding + API               |

Stripe payment links for paid tiers are configured via environment variables (`STRIPE_LINK_DANGEROUS`, `STRIPE_LINK_BADDIE`, `STRIPE_LINK_CEO`). Freemium gate logic lives in `src/monetization/whatsapp_paywall.py` and never activates payment without a verified Stripe event.

## Ad Copy Matrix
- **Headline 1:** Saphira AI: Speak Upfront. Automate in Silence.
- **Headline 2:** The Conversational AI Created by Chelsea Megan Woods
- **Primary Text:** Stop toggling between 10 different apps. Talk to Saphira naturally while she silently runs your code, manages 3D printers, and controls your smart home in the background. Simplify your day by 1% every single time.
- **Targeting:** Tech professionals, entrepreneurs, creators, smart home enthusiasts, automation seekers.
- **Negative Keywords:** free download crack, open source clone, free github bot, cheap template.
