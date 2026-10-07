import json
import os

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow any website to call this endpoint (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the data once, from the file bundled with the deployment
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")
with open(DATA_PATH) as f:
    DATA = json.load(f)


@app.post("/")
async def analyze(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    result = {}
    for region in regions:
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            continue
        latencies = np.array([r["latency_ms"] for r in rows], dtype=float)
        uptimes = np.array([r["uptime_pct"] for r in rows], dtype=float)

        result[region] = {
            "avg_latency": float(latencies.mean()),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(uptimes.mean()),
            "breaches": int((latencies > threshold).sum()),
        }
    return result