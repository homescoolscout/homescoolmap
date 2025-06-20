from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for iframe
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

@app.on_event("startup")
async def startup():
    app.state.db = await asyncpg.connect(DATABASE_URL)
    await app.state.db.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            city TEXT,
            state TEXT,
            country TEXT,
            lat DOUBLE PRECISION,
            lng DOUBLE PRECISION
        )
    """)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

@app.get("/locations")
async def get_locations():
    rows = await app.state.db.fetch("SELECT city, state, country, lat, lng FROM locations")
    return [dict(r) for r in rows]

@app.post("/locations")
async def add_location(request: Request):
    data = await request.json()
    await app.state.db.execute("""
        INSERT INTO locations (city, state, country, lat, lng)
        VALUES ($1, $2, $3, $4, $5)
    """, data["city"], data["state"], data["country"], data["lat"], data["lng"])
    return {"status": "ok"}
