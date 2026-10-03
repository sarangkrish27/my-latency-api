import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets any website call your endpoint from a browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the data once, from the file sitting next to this script
DATA = json.loads((Path(__file__).parent / "q-vercel-latency.json").read_text())


@app.post("/")
@app.post("/api")
def analyze(body: dict):
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}
    for region in regions:
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            continue
        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]
        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for x in latencies if x > threshold),
        }

    # Region results are available both at the top level and under "regions"
    return {**result, "regions": result}