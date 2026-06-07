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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "q-vercel-latency.json")
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
        uptimes = [r["uptime_pct"] for r in records]
        
        # Calculate 95th percentile
        sorted_lat = sorted(latencies)
        idx = (len(sorted_lat) - 1) * 0.95
        low, high = int(idx), min(int(idx) + 1, len(sorted_lat) - 1)
        p95 = sorted_lat[low] + (sorted_lat[high] - sorted_lat[low]) * (idx - low)
        
        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 4),
            "p95_latency": round(p95, 4),
            "avg_uptime": round(statistics.mean(uptimes), 4),  # Removed / 100
            "breaches": sum(1 for l in latencies if l > req.threshold_ms),
        }
    return result