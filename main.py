
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI()

# Allow all origins for Wix iframe access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path("locations.json")

@app.get("/locations")
def get_locations():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

@app.post("/locations")
async def add_location(req: Request):
    data = await req.json()
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w") as f:
            json.dump([data], f)
    else:
        with open(DATA_FILE, "r+") as f:
            existing = json.load(f)
            existing.append(data)
            f.seek(0)
            json.dump(existing, f, indent=2)
    return {"status": "ok"}
