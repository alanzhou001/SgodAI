# SgodAI Market Radar

SgodAI Market Radar is a local-first, AI-assisted market intelligence and investment research support system. It is designed for structured research workflows: collecting market information, normalizing events, scoring signals, identifying position observation windows, generating reports, and sending alerts.

It is not a news feed, stock-tipping product, or automated trading system.

> Disclaimer: This system does not constitute investment advice. It does not provide automated trading, direct buy/sell instructions, or return guarantees. All outputs are for research leads, information organization, risk awareness, and decision support only.

## What Is Included

- Product PRD: [docs/PRD.md](docs/PRD.md)
- Technical design: [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)
- Apple-first interactive demo: [public/index.html](public/index.html)
- Local-first Python Core Engine skeleton: [app/](app/)
- Future-ready config examples: [configs/](configs/)
- Minimal tests: [tests/](tests/)

## Architecture Position

```text
Core Engine = facts, data, state, scoring, window detection, storage, delivery
Agent Copilot = explanation, summary, attribution, research, Q&A, coordination
```

The Core Engine remains useful when LLM or Agent capabilities are disabled. All AI output must be grounded in source events, evidence fields, confidence values, and risk notes.

## Run The Frontend Demo

Open the static demo directly:

```text
public/index.html
```

Or serve it locally:

```bash
python3 -m http.server 5173 -d public
```

Then visit:

```text
http://127.0.0.1:5173
```

The demo is dependency-free and optimized for Safari/macOS style interaction. It uses mock data but keeps explicit adapter boundaries for future real data providers.

## Run Core Checks

```bash
python3 -m unittest discover -s tests
```

## Suggested Directory Layout

```text
app/
  main.py
  settings.py
  db/
  models/
  services/
  providers/
  scoring/
  reports/
  notifications/
  agents/
  llm/
  knowledge_graph/
  api/
configs/
  config.yaml
  sources.yaml
  watchlist.yaml
  sectors.yaml
  email_targets.yaml
  llm.yaml
  agents.yaml
data/
tests/
scripts/
public/
```

## MVP Roadmap

1. M1: Watchlist, Asset model, provider interfaces, event database, SQLite storage, basic UI.
2. M2: Event normalization, classification, scoring, event cards.
3. M3: Report composer, post-market report, weekly report, email targets, delivery logs.
4. M4: Position Window Engine, auditable state transitions, status explanations.
5. M5: AI Research Assistant, LLM provider interface, grounded report and window explanations.

