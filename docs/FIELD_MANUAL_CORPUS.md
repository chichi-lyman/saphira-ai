# Public-Domain Field Manual Corpus — Training Doctrine

**Copyright © 2026 Chelsea Megan Woods**  
**System:** saphira-ai / Nova Umbrella

How Saphira and all agents gain **unclassified, publicly released** U.S. government and military field knowledge for survival, austere medicine, navigation, and situational awareness—**without** restricted or classified sources.

This is a **corpus map and ingestion blueprint**, not a dump of manual text. Agents retrieve principles via offline RAG when vault packs are installed; they do not invent classified TTPs.

Related: [LOCALIZED_SPARK_PROTOCOL.md](./LOCALIZED_SPARK_PROTOCOL.md) · [KINETIC_DEFENSE_SUSTENANCE.md](./KINETIC_DEFENSE_SUSTENANCE.md) · [AEMP_AEGIS_EVASION_MEDICAL.md](./AEMP_AEGIS_EVASION_MEDICAL.md) · [VERIFIABLE_ORACLE.md](./VERIFIABLE_ORACLE.md)

---

## Primary open sources

| Source | URL (public) | Use |
|--------|----------------|-----|
| Army Publishing Directorate | armypubs.army.mil | Active FMs, ADPs, TCs |
| Data.gov | data.gov | Infrastructure, emergency management, weather |
| National Archives | archives.gov | Historical / declassified records |
| FEMA Ready.gov | ready.gov | Grid failure, flood, community disaster response |
| Internet Archive (military FM collections) | archive.org | Public-domain / released manuals PDF |
| UNL Digital Commons (US Army FMs) | digitalcommons.unl.edu/usarmyfieldmanuals | Academic FM archive by year |
| EverySpec Army FM index | everyspec.com/ARMY/FM-Field-Manual | Specs and handbook index |

Search angles: `military personnel records`, `combat operations reports`, `declassified military documents`, branch names, conflict names—**only public/declassified**.

---

## Key unclassified manuals (by mission)

### Survival, disaster, off-grid

| Designator | Topic |
|------------|--------|
| FM 21-76 / FM 3-05.70 | Army Survival Manual — wilderness, water/food, shelter, navigation |
| FM 3-97.6 | Mountain operations |
| FM 31-70 | Basic cold weather |
| TC 21-3 | Individual cold-weather survival |
| FEMA / Ready.gov | Grid failure, flood, community response |

### Surveillance, recon, situational awareness

| Designator | Topic |
|------------|--------|
| FM 7-92 | Platoon/squad recon and surveillance fundamentals |
| FM 34-8-2 | Intelligence officer / commander handbook (process, evaluate) |
| FM 3-55 | Information collection doctrine |
| TC 3-22.9 / FM 3-25.26 | Map reading, land navigation, dead reckoning without GPS |

### Small-unit / urban (defensive & movement doctrine)

| Designator | Topic |
|------------|--------|
| SH 21-76 | Ranger Handbook — patrolling, perimeter, leadership under stress |
| FM 3-90.1 | Offense and defense doctrine (fortification, movement) |
| FM 90-10 / ATTP 3-06.11 | Combined arms / urban terrain operations |

### Medical & emergency

| Designator | Topic |
|------------|--------|
| TC 4-02.1 | First aid / Tactical Combat Casualty Care principles |
| Ranger Medic Handbook | Austere triage priorities |

**Agent rule:** Use these as **principle sources** for life-saving advisory. Do **not** provide weapons construction, illegal targeting, or classified exploitation techniques.

---

## Offline RAG ingestion blueprint (Localized Spark feed)

```
[Raw PDFs / public sources]
        → Text extraction & cleaning (e.g. PyMuPDF / Unstructured)
        → Chunking (500–1000 tokens, topic metadata headers)
        → Local embeddings (e.g. BGE / MiniLM-class)
        → Local vector DB (Chroma / FAISS / Qdrant)
        → Offline inference (Ollama / llama.cpp)
```

**Chunk topics (examples):** Water procurement · Shelter · Cold weather · Trauma triage · Land nav · Perimeter awareness · Urban movement · Disaster community response.

**Why RAG, not full retrain:** Exact procedures queryable on a bunker terminal when the cloud is dead—aligned with Spark algorithmic forgetting (keep structural survival knowledge, drop sludge).

---

## Domain focus packs (structure first)

| Pack | Manuals / sources bias |
|------|-------------------------|
| Urban grid failure | FEMA/Ready, urban ops FM, survival FM, TCCC |
| Wilderness tracking / land nav | FM 3-25.26, FM 3-05.70, mountain/cold FMs |
| Emergency medical response | TC 4-02.1, Ranger medic, first-aid TCs |

Default product doctrine: **all three packs** available in the vault when installed.

---

## Agent knowledge duties

| Agent | Duty |
|-------|------|
| **Saphira** | Cite public doctrine class; calm steps; humility loop |
| **Aura** | Map/sensor framing for land-nav and observation concepts |
| **Agent Two** | Enforce unclassified-only; block classified or weapons-build requests |
| **Nova Reign** | Route survival queries to vault RAG nodes when offline mode set |
| **NovaAethrea** | Index chunk metadata; prune non-survival mass in Spark mode |
| **Agent Zero** | Local vector DB / Ollama-style offline stack engineering |
| **Lyra** | Nav math, ration and environmental calculations from doctrine |
| **Cipher** | Air-gapped vault integrity; no exfil of crisis sessions |
| **Lexis** | Public-domain / government work licensing awareness |
| **Instinct** | Tone for trauma without panic amplification |
| **Scholar** | Teach which FM covers which skill; source literacy |
| **Apex** | Humanitarian / resilience packaging—not militarized harm markets |

## Invariants

- Unclassified and public only  
- Life-preserving advisory; no abandonment; no weapons construction  
- Humans retain ethical and deployment authority  
- Copyright © 2026 Chelsea Megan Woods  
