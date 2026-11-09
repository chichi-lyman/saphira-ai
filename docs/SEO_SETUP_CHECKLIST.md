# SEO Setup Checklist — Complete

**© 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella**

Repo-side pipeline is **complete**. Remaining items require account access only you control.

---

## Done in repository (automated / committed)

- [x] `llms.txt` — LLM-optimized architecture + credentials summary
- [x] `public/schema/person-saphira.jsonld` — Person + SoftwareApplication + Organization graph
- [x] `public/schema/embed-snippet.html` — ready-to-paste `<script type="application/ld+json">`
- [x] `public/sitemap.xml.template` — custom-domain sitemap starter
- [x] `robots.txt` — explicit allow for major AI crawlers
- [x] `docs/SEO_AND_DISCOVERABILITY.md` — full strategy
- [x] `.github/workflows/indexnow-ping.yml` — IndexNow on docs/release changes
- [x] README Discoverability section + recommended topics list

---

## Remaining (your accounts — ~10 minutes)

### 1. GitHub repository topics

1. Open https://github.com/chichi-lyman/saphira-ai  
2. Click the gear next to **About** (or Settings → General)  
3. Add these topics (copy-paste):

```
multi-agent-systems
edge-ai
fastapi
saphira-ai
webgpu
onnx
voice-assistant
nova-umbrella
android
flutter
pgvector
```

4. Optional: set Homepage to your Beacons or portfolio URL

### 2. IndexNow key (Bing → ChatGPT Search, Copilot, Perplexity)

1. Generate a key: https://www.indexnow.org/documentation#key  
2. Repo → **Settings → Secrets and variables → Actions → New repository secret**  
   - Name: `INDEXNOW_KEY`  
   - Value: your key  
3. If you own a custom domain, host `https://YOUR-DOMAIN/{key}.txt` containing only the key  
4. Re-run **IndexNow & Discoverability Ping** workflow (Actions → Run workflow)

### 3. Google Search Console

1. https://search.google.com/search-console  
2. Add every custom domain you own (Beacons custom domain, portfolio, Shopify, etc.)  
3. Verify ownership (DNS or HTML tag)  
4. Submit sitemap: use `public/sitemap.xml.template` → host as `/sitemap.xml` → paste URL into GSC  
5. Request indexing for the homepage and `/llms.txt`

### 4. Embed JSON-LD on public pages

Copy the full contents of:

`public/schema/embed-snippet.html`

Paste into:

- Beacons page custom HTML / head injection  
- Portfolio / GitHub Pages `<head>`  
- Any product or case-study landing page  

### 5. Cross-link social entity graph

Ensure these profiles all link to each other and to https://github.com/chichi-lyman :

| Platform | URL |
|----------|-----|
| GitHub | https://github.com/chichi-lyman |
| Beacons | https://beacons.ai/chichi-lyman |
| TikTok | https://www.tiktok.com/@chelseameganwoods |
| Instagram | https://www.instagram.com/chelsiaaa.woods |

### 6. (Optional) First technical article

Publish one deep-dive on Medium or Dev.to, e.g.:

> Architecting a Multi-Agent Executive Runtime (Saphira / Nova Umbrella)

Include direct links to the monorepo and `llms.txt`. That creates the external citation graph search engines reward.

---

## Verification

After the steps above:

- [ ] Topics visible on the repo About box  
- [ ] IndexNow workflow runs green with key configured  
- [ ] GSC shows verified property + submitted sitemap  
- [ ] View-source on Beacons/portfolio contains `application/ld+json` with Chelsea Megan Woods + Saphira AI  
- [ ] Social bios link back to GitHub  

When those five are checked, the discoverability pipeline is fully operational.
