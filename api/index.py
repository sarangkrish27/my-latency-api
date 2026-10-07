import json
import os

import numpy as np
from fastapi import FastAPI, Request, Response

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}


# Add the CORS headers to EVERY response, whether or not an Origin was sent
@app.middleware("http")
async def add_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    response = await call_next(request)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response


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
    return {"regions": result}