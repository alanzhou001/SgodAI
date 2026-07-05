# SgodAI Market Radar

SgodAI Market Radar is a local-first, AI-assisted market intelligence and investment research support system. It is designed for structured research workflows: collecting market information, normalizing events, scoring signals, identifying position observation windows, generating reports, and sending alerts.

It is not a news feed, stock-tipping product, or automated trading system.

> Disclaimer: This system does not constitute investment advice. It does not provide automated trading, direct buy/sell instructions, or return guarantees. All outputs are for research leads, information organization, risk awareness, and decision support only.

## License

SgodAI Market Radar is licensed under the Business Source License 1.1
(`BUSL-1.1`) starting from versions released after this license change. The
source is available for personal, non-commercial research, academic research,
internal evaluation, development, testing, and demonstration. Commercial
production use, hosted services, managed services, paid research platforms,
investment advisory services, commercial data products, or competing commercial
offerings require a separate commercial license from the licensor.

The Change Date is `2030-07-06`. On that date, or earlier if required by the
Business Source License 1.1 terms for a specific version, the licensed work
changes to the MIT License. Earlier releases remain available under the license
terms that applied to those releases.

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

## Build macOS App

SgodAI includes a native SwiftUI + WebKit macOS shell under
`macos/SgodAI-Mac`. Starting with v0.2.1, the release app embeds a bundled
Python Core Engine binary and starts it automatically on
`http://127.0.0.1:18765/`. Users no longer need to start `uvicorn` before
opening the app. If the embedded API cannot start, the app falls back to the
bundled static frontend.

Build with Xcode 27 beta when available:

```bash
scripts/build_macos_app.sh
```

The release artifact is generated at:

```text
dist/SgodAI-Market-Radar-macOS-v0.2.1.zip
```

The installed app keeps user-local state under:

```text
~/Library/Application Support/SgodAI/
  .env
  data/sgodai.sqlite
  logs/backend.log
```

Fill `.env` there when you want DeepSeek or QQ Mail from the installed app.
This macOS package is intentionally unsigned and not notarized. For wider
distribution, add an Apple Developer Team ID and notarization step before
publishing outside GitHub releases.

## Real Data + DeepSeek Setup

The first real-data profile is DeepSeek + AkShare + RSSHub + CNINFO + HKEXnews,
focused on A-share and HK equities.

1. Create a local environment file:

```bash
cp .env.example .env
```

Fill at least:

```bash
DEEPSEEK_API_KEY=sk-...
```

The default DeepSeek OpenAI-compatible endpoint is `https://api.deepseek.com`, with `deepseek-v4-flash` as the low-latency research assistant model.

2. Install optional real-data dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[realdata]"
```

3. Review local config:

- LLM: [configs/llm.yaml](configs/llm.yaml)
- Data sources: [configs/sources.yaml](configs/sources.yaml)
- Watchlist: [configs/watchlist.yaml](configs/watchlist.yaml)

4. Start the local API:

```bash
uvicorn app.api.server:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the local frontend. API routes remain under `/api/*`.

5. Quick checks:

```bash
curl http://127.0.0.1:8000/api/health
curl "http://127.0.0.1:8000/api/assets/688525.SH/ohlcv"
curl "http://127.0.0.1:8000/api/news/rss?query=半导体"
curl "http://127.0.0.1:8000/api/disclosures/announcements?ticker=688525.SH"
curl "http://127.0.0.1:8000/api/disclosures/reports?ticker=700.HK"
```

Default public-source coverage:

- News: RSSHub routes for 财联社、第一财经、证券时报、新浪财经、证监会、财新最新.
- A-share disclosures and reports: CNINFO title search and PDF links.
- HK disclosures and reports: HKEXnews title search and PDF links.

Public sources are suitable for MVP research workflows, not hard real-time or SLA-bound production.
If a paid/authorized data API becomes necessary, add it as a new provider behind the same local API.

## QQ Mail SMTP Setup

The MVP email channel uses QQ Mail SMTP by default.

1. Open QQ Mail settings and enable SMTP service.
2. Generate an SMTP authorization code.
3. Fill `.env`:

```bash
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_USERNAME=your_qq_mail@qq.com
SMTP_PASSWORD=your_qq_mail_smtp_authorization_code
SMTP_FROM=your_qq_mail@qq.com
SMTP_FROM_NAME=SgodAI Market Radar
```

Do not use your QQ login password as `SMTP_PASSWORD`; use the SMTP authorization code.

After starting the local API, use the email settings page to send a test email, or call:

```bash
curl http://127.0.0.1:8000/api/notifications/email/config
```

## Publish To GitHub

After GitHub CLI authentication is valid:

```bash
gh auth login -h github.com -p https -w
./scripts/publish_github.sh SgodAI
```

The helper creates a public GitHub repository, adds `origin`, pushes `main`, and sets upstream tracking.

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
