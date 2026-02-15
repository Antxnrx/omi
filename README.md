# Baby Sleep Sync (Omi Hackathon MVP)

A lightweight demo app for automatic baby sleep/cry tracking powered by transcript webhooks from the **Omi AI circular pendant**.

## What it demonstrates
- Real-time transcript webhook ingestion from the Omi circular pendant audio stream.
- Rule-based cry classification (`hungry`, `tired`, `discomfort`, `pain`, `unknown`).
- Auto-generated insight (e.g., **"Last feed was X hours ago"**) when hunger cries are detected.
- Live dashboard with event stream, sleep pattern view, and simple summary cards.
- Simulated Huckleberry sync endpoint for demo storytelling.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

In another terminal:

```bash
python -m http.server 8080
```

Open `http://localhost:8080/dashboard.html`.

## API Endpoints
- `POST /webhook/omi/transcript`: ingest transcript text.
- `GET /summary`: aggregate counts + recent events.
- `GET /insights`: generated insights.
- `POST /demo/populate`: seed demo timeline.
- `DELETE /demo/clear`: clear in-memory events.
- `POST /sync/huckleberry`: simulated export payload.

## Device Context
This MVP is explicitly designed for the **Omi AI circular pendant** wearable experience (always-on passive capture + transcript webhooks).

## Suggested 2-minute Demo Flow
1. Click **Populate Demo Data**.
2. Show cry classification + sleep/wake patterns.
3. Highlight insight card for feed timing.
4. Click **Sync to Huckleberry** to show simulated export.
