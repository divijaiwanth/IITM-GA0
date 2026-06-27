# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi",
#   "uvicorn",
# ]
# ///

import csv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Load CSV once at startup
students = []
with open("q-fastapi.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        students.append({
            "studentId": int(row["studentId"]),
            "class": row["class"]
        })

@app.get("/api")
async def get_students(
    class_: Optional[List[str]] = Query(default=None, alias="class")
):
    if class_:
        filtered = [s for s in students if s["class"] in class_]
        return {"students": filtered}
    return {"students": students}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)