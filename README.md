# 405 Network — Property Investment Analyzer

**Make smarter property investment decisions in seconds.** Paste a listing, get an instant verdict.

🚀 **[Live Demo](https://property-calculator.azurewebsites.net/)**

## What It Does

1. **Paste** a property listing (text or URL) into the chat
2. **Parse** — AI extracts 16 structured fields in real-time (7-step pipeline)
3. **Analyze** — 7 investment metrics calculated instantly (Cap Rate, CoC, DSCR, NOI, Price/Unit, Break-Even, GRM)
4. **Verdict** — ✅ INVEST / ⚠️ REVIEW / ❌ PASS with 3 supporting reasons
5. **Save** — One click saves to your team's Google Sheet portfolio
6. **Share** — Every analysis has a unique URL with all state preserved

## Tech Stack

- **Backend**: FastAPI (Python 3.11) — serves API + UI from one process
- **Frontend**: HTMX + Jinja2 + Tailwind/DaisyUI — no React, no build step
- **Parser**: Azure OpenAI (gpt-4o) + Rentcast API + Playwright
- **Data**: Google Sheets (gspread with service account)
- **Deployment**: Azure App Service + GitHub Actions CI/CD

## Quick Start

```bash
git clone https://github.com/vyente-ruffin/property-calculator.git
cd property-calculator
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your API keys
uvicorn server:app --host 0.0.0.0 --port 8090 --reload
```

Open http://localhost:8090

## Features

- 🏢 Commercial (5+ units) and 🏡 Residential (≤4 units) analysis
- 🌙 Dark mode (default) and ☀️ Light mode toggle
- 📱 Responsive — desktop, tablet, and mobile
- 🔗 Shareable URLs — every analysis is bookmarkable
- 📊 Portfolio — browse and compare all saved deals
- 🖼️ Rich link previews — OG tags for SMS/social sharing

## Supported Markets

AZ, CA, IN, NV, TX, MI — with state-specific tax and insurance rates.