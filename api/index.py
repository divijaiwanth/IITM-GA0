# api/index.py
import json
import os
import statistics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS so any website can call our endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow any website
    allow_methods=["POST"],    # Only allow POST requests
    allow_headers=["*"],
)

# Load the telemetry data once when the function starts
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")
with open(DATA_FILE) as f:
    RAW_DATA = json.load(f)

# Define what the incoming request body looks like
class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/analytics")
def analytics(req: AnalyticsRequest):
    result = {}

    for region in req.regions:
        # Filter data to only records matching this region
        records = [r for r in RAW_DATA if r["region"] == region]

        if not records:
            result[region] = None
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes   = [r["uptime"] for r in records]

        # Sort latencies to calculate p95
        sorted_latencies = sorted(latencies)
        p95_index = int(len(sorted_latencies) * 0.95)  # 95% of the way through
        p95 = sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]

        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 4),
            "p95_latency": round(p95, 4),
            "avg_uptime":  round(statistics.mean(uptimes), 4),
            "breaches":    sum(1 for l in latencies if l > req.threshold_ms),
        }

    return result