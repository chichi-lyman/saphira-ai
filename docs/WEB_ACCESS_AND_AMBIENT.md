# Saphira Web Access, Synthesis & Ambient Capabilities
**Version:** 1.1  
**Copyright © 2026 Chelsea Megan Woods**  
**Parent:** Nova Umbrella / Woods Legacies / Saphira AI

## Scope & Hard Boundaries

- Public web only. robots.txt is checked on every host.
- Rate-limited, identified User-Agent, max pages per host enforced.
- **No login bypass, CAPTCHA solving, paywall circumvention, or authenticated deep-web access.** These are permanently out of scope.
- All network and device actions pass Agent Two + policy gates.
- Surface output never exposes crawler internals, agent names, or raw HTML.

## Capability Surface

| Capability ID | Description | Primary Agent |
|---------------|-------------|----------------|
| `web_search` | Query search API, return titles + links + snippets | Agent Scholar |
| `fetch_page` | Responsible single-page fetch after robots check | Agent Scholar |
| `refresh_page` | Incremental re-fetch of a previously seen URL | Agent Scholar |
| `synthesize_research` | Multi-source summary, entities, patterns, structured brief | Agent Scholar → Synthesis |
| `cast_to_display` | Push map / article / image to nearby TV or smart display | Agent Zero |
| `push_to_device` | Open map or article on phone / laptop | Agent Zero |
| `start_trivia` | Spontaneous topic-based trivia round | Agent Scholar / game worker |
| `set_ambient_music` | Queue background music matching conversation tone | Agent Zero |

## Pipeline Placement

```
User utterance
  → Saphira (intent)
  → Aura (perception / topic enrichment)
  → Agent Two (security + domain allow-list + rate budget)
  → NovaReign (capability routing)
  → NovaAethrea (memory read/write of durable facts)
  → Agent Zero / Scholar (execution of tools)
  → Synthesis (if research)
  → Samantha translator → surface only
```

## Module Layout

```
src/tools/
  search/web_search.py
  crawler/responsible_crawler.py
  synthesis/data_synthesis.py
  ambient/
    casting.py
    trivia.py
    music.py
```
