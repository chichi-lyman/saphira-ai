# Saphira Local Setup — Web Access, Synthesis & Ambient (v1.1)

**Copyright © 2026 Chelsea Megan Woods**

## 1. Prerequisites

```bash
git clone https://github.com/chichi-lyman/saphira-ai.git
cd saphira-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install httpx beautifulsoup4 pytest pytest-asyncio   # recommended for new modules
```

## 2. Environment (.env)

```bash
# Search (choose one)
SERPER_API_KEY=
SAPHIRA_SEARCH_PROVIDER=serper

# Home Assistant (casting, music, smart devices)
HA_LONG_LIVED_TOKEN=
HA_WS_URL=ws://homeassistant.local:8123/api/websocket
SAPHIRA_DEFAULT_CAST_ENTITY=media_player.living_room_tv
SAPHIRA_DEFAULT_MUSIC_ENTITY=media_player.living_room

# Security gate
SECURITY_PIN=
AUTO_APPROVE_LIMIT=25.0
```

## 3. Smoke tests

```bash
pytest tests/test_responsible_crawler.py -q

python -c "from src.tools.search.web_search import web_search; print('search ok')"
python -c "from src.tools.synthesis.data_synthesis import synthesize_research; print('synth ok')"
python -c "from src.core.policy import require_security_gate; print('policy ok')"
python -c "from src.core.orchestrator import run_pipeline; print('orchestrator ok')"
```

## 4. New module locations

| Path | Purpose |
|------|---------|
| `src/tools/crawler/responsible_crawler.py` | Focused + incremental crawler |
| `src/tools/search/web_search.py` | Search API adapter |
| `src/tools/synthesis/data_synthesis.py` | Multi-source synthesis |
| `src/tools/ambient/casting.py` | Cast + device push |
| `src/tools/ambient/trivia.py` | Topic trivia |
| `src/tools/ambient/music.py` | Ambient music |
| `src/core/capability_entries_web.py` | Registry entries |
| `src/core/orchestrator.py` | Fixed 6-stage pipeline |
| `src/core/policy.py` | Authority policy + audit |
| `docs/WEB_ACCESS_AND_AMBIENT.md` | Architecture & boundaries |

## 5. Hard boundaries

- Public web only
- robots.txt always checked
- No login bypass / CAPTCHA / paywall circumvention
- All actions still pass Agent Two + policy gates
- Internal agent names never surface to the user
