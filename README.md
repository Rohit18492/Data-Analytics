# PathForge SSOT — 6-Month Data Engineering + Databricks + Fabric + GenAI

Interactive, **self-contained** learning system for an experienced Qlik/BI engineer (12+ years) targeting **Senior Data & AI Analytics Consultant / Data & AI Architect**.

## Open the artifact

Open `index.html` in a desktop browser (Chrome/Edge/Firefox). Progress, notes, bookmarks, quiz history, and hours persist in **localStorage** (this browser profile only).

No backend. No required CDN libraries. Optional: serve locally if your browser restricts `file://` script loading:

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080`.

## What is inside

- 6-month curriculum mapped to:
  - **Databricks Certified Data Engineer Associate** exam guide **as of 4 May 2026** (7 sections, Lakeflow, Git Folders, Automation Bundles, UC ABAC, Liquid Clustering, predictive optimization)
  - **DP-700 Fabric Data Engineer Associate** skills measured **as of 21 July 2026**
- Qlik → modern DE skill bridge
- 180-day study plan (12–14 h/week)
- Quiz engine (1000+ original practice items — **not** real exam questions)
- 5 mock-style draws each for Databricks (45 Q) and DP-700 (50 Q)
- Flashcards, glossary, interview bank (senior/architect bias), 8 industry projects + capstone
- 50 enterprise scenarios, 50 debug labs, 30 architecture labs
- Certification tracker, change log, 30-day bootcamps, interview simulator, freelance kits

## Certification notice

This artifact is a structured preparation system designed around the official certification objectives. **Completing it does not guarantee certification.** Validate readiness with official practice assessments and hands-on platform work.

Official sources (verified 18 Aug 2026):

- https://www.databricks.com/learn/certification
- https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026-000.pdf
- https://learn.microsoft.com/en-us/credentials/certifications/fabric-data-engineer-associate/
- https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/dp-700

## Regenerating content

Python generators live in `tools/`. Re-run them only if you intend to rebuild question banks.

## Privacy

Notes and scores never leave your browser. Do not put cloud secrets into the Notes fields if you share the machine.
