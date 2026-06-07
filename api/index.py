import json
import os
import statistics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")
with open(DATA_FILE) as f:
    RAW_DATA = json.load(f)

class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/analytics")
def analytics(req: AnalyticsRequest):
    result = {}
    for region in req.regions:
        records = [r for r in RAW_DATA if r["region"] == region]
        if not records:
            result[region] = None
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]
        sorted_lat = sorted(latencies)
        p95 = sorted_lat[min(int(len(sorted_lat) * 0.95), len(sorted_lat) - 1)]
        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 4),
            "p95_latency": round(p95, 4),
            "avg_uptime": round(statistics.mean(uptimes), 4),
            "breaches": sum(1 for l in latencies if l > req.threshold_ms),
        }
    return result