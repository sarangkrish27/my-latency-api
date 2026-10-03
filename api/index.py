
import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from every origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load the supplied telemetry data
DATA_PATH = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

with open(DATA_PATH, "r") as f:
    data = json.load(f)


@app.post("/")
def analyze(body: dict):
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}

    for region in regions:

        records = [
            row for row in data
            if row["region"] == region
        ]

        if not records:
            continue

        latencies = [
            row["latency_ms"] for row in records
        ]

        uptimes = [
            row["uptime_pct"] for row in records
        ]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(
                sum(x > threshold for x in latencies)
            )
        }

    return result