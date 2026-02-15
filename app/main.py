from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Baby Sleep Sync")

# In-memory storage for fast demo iteration
events: List[Dict] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def classify_simple(text: str) -> str:
    """Simple rule-based cry classification for hackathon MVP."""
    if any(word in text for word in ["hungry", "feed", "milk", "bottle"]):
        return "hungry_cry"
    if any(word in text for word in ["tired", "sleepy", "nap"]):
        return "tired_cry"
    if any(word in text for word in ["diaper", "wet", "rash", "gas"]):
        return "discomfort_cry"
    if any(word in text for word in ["pain", "hurt", "fever"]):
        return "pain_cry"
    return "unknown_cry"


def parse_event_from_text(text: str) -> Optional[Dict]:
    lower_text = text.lower()
    timestamp = now_iso()

    if "fed" in lower_text or "feeding" in lower_text or "bottle" in lower_text:
        return {
            "type": "feed_detected",
            "timestamp": timestamp,
            "text": lower_text,
        }

    if "cry" in lower_text or "crying" in lower_text:
        return {
            "type": "cry_detected",
            "timestamp": timestamp,
            "classification": classify_simple(lower_text),
            "text": lower_text,
        }

    if any(word in lower_text for word in ["asleep", "sleeping", "fell asleep", "nap"]):
        return {
            "type": "sleep_detected",
            "timestamp": timestamp,
            "text": lower_text,
        }

    if any(word in lower_text for word in ["awake", "woke up", "wakeup", "waking"]):
        return {
            "type": "wake_detected",
            "timestamp": timestamp,
            "text": lower_text,
        }

    return None


def extract_last_feed_gap_hours() -> Optional[float]:
    feed_events = [e for e in events if e["type"] == "feed_detected"]
    if not feed_events:
        return None

    last_feed_ts = datetime.fromisoformat(feed_events[-1]["timestamp"])
    gap = datetime.now() - last_feed_ts
    return round(gap.total_seconds() / 3600, 1)


@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "Baby Sleep Sync API Running"}


@app.post("/webhook/omi/transcript")
async def handle_transcript(request: Request) -> Dict[str, object]:
    """Receive transcript payloads from Omi and detect baby-care events."""
    data = await request.json()
    text = data.get("text", "")

    event = parse_event_from_text(text)
    generated_insight = None

    if event:
        events.append(event)

        if event["type"] == "cry_detected" and event.get("classification") == "hungry_cry":
            last_feed_gap = extract_last_feed_gap_hours()
            if last_feed_gap is not None:
                generated_insight = f"Last feed was {last_feed_gap} hours ago"

    return {
        "status": "processed",
        "detected": bool(event),
        "event": event,
        "insight": generated_insight,
        "events_count": len(events),
    }


@app.get("/events")
def get_events() -> Dict[str, object]:
    return {"events": events, "count": len(events)}


@app.get("/summary")
def get_summary() -> Dict[str, object]:
    cry_events = [e for e in events if e["type"] == "cry_detected"]
    sleep_events = [e for e in events if e["type"] == "sleep_detected"]
    wake_events = [e for e in events if e["type"] == "wake_detected"]
    feed_events = [e for e in events if e["type"] == "feed_detected"]

    return {
        "total_events": len(events),
        "cries": len(cry_events),
        "sleep_events": len(sleep_events),
        "wake_events": len(wake_events),
        "feeds": len(feed_events),
        "events": events[-15:],
    }


@app.get("/insights")
def get_insights() -> Dict[str, object]:
    cry_events = [e for e in events if e["type"] == "cry_detected"]
    hungry_cries = [e for e in cry_events if e.get("classification") == "hungry_cry"]

    insights = []
    if len(hungry_cries) >= 2:
        insights.append(
            {
                "type": "pattern",
                "icon": "🍼",
                "message": f"Detected {len(hungry_cries)} hunger cries today.",
            }
        )

    if len(events) >= 5:
        insights.append(
            {
                "type": "success",
                "icon": "✅",
                "message": "Great tracking coverage for your demo day.",
            }
        )

    last_feed_gap = extract_last_feed_gap_hours()
    if last_feed_gap is not None:
        insights.append(
            {
                "type": "timing",
                "icon": "⏱️",
                "message": f"Last feed was {last_feed_gap} hours ago.",
            }
        )

    return {"insights": insights}


@app.post("/demo/populate")
def populate_demo_data() -> Dict[str, object]:
    global events
    now = datetime.now()

    demo_events = [
        {
            "type": "feed_detected",
            "timestamp": (now - timedelta(hours=3, minutes=10)).isoformat(timespec="seconds"),
            "text": "fed baby 4oz bottle",
        },
        {
            "type": "cry_detected",
            "timestamp": (now - timedelta(hours=3)).isoformat(timespec="seconds"),
            "classification": "hungry_cry",
            "text": "baby crying and sounds hungry",
        },
        {
            "type": "sleep_detected",
            "timestamp": (now - timedelta(hours=2, minutes=45)).isoformat(timespec="seconds"),
            "text": "baby fell asleep after feeding",
        },
        {
            "type": "wake_detected",
            "timestamp": (now - timedelta(minutes=40)).isoformat(timespec="seconds"),
            "text": "baby woke up from nap",
        },
        {
            "type": "cry_detected",
            "timestamp": (now - timedelta(minutes=35)).isoformat(timespec="seconds"),
            "classification": "discomfort_cry",
            "text": "baby crying, might need diaper change",
        },
    ]

    events.extend(demo_events)
    return {"message": "Demo data added", "count": len(demo_events), "events_total": len(events)}


@app.delete("/demo/clear")
def clear_demo_data() -> Dict[str, str]:
    global events
    events = []
    return {"message": "All demo data cleared"}


@app.post("/sync/huckleberry")
def sync_to_huckleberry_simulated() -> Dict[str, object]:
    """Simulate export payload that could be sent to Huckleberry."""
    export_events = [
        {
            "event": e["type"],
            "time": e["timestamp"],
            "note": e.get("classification") or e.get("text", ""),
        }
        for e in events[-20:]
    ]
    return {
        "status": "simulated",
        "destination": "Huckleberry",
        "exported_count": len(export_events),
        "preview": export_events[:5],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
