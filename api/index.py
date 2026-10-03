import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()


# Add CORS headers to EVERY response, whether or not the request has an Origin
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


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

    return {**result, "regions": result}

@app.options("/{path:path}")
def preflight(path: str = ""):
    return Response(status_code=200)