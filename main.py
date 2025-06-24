# src/main.py

import os
import psycopg2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Correct database URL from Render
DATABASE_URL = "postgresql://homescool_user:dDQndv58MobGiZzxeaWgWmmUGLG8zyaP@dpg-d1aq6vuuk2gs7391ss2g-a.oregon-postgres.render.com/homescool"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Location(BaseModel):
    city: str
    state: str
    country: str
    lat: float
    lng: float
    name: str = ""

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            city TEXT,
            state TEXT,
            country TEXT,
            lat DOUBLE PRECISION,
            lng DOUBLE PRECISION,
            name TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

@app.post("/locations")
async def add_location(location: Location):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO locations (city, state, country, lat, lng, name)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (location.city, location.state, location.country, location.lat, location.lng, location.name))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Location saved"}

@app.get("/locations")
async def get_locations():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT city, state, country, lat, lng, name FROM locations;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "city": row[0],
            "state": row[1],
            "country": row[2],
            "lat": row[3],
            "lng": row[4],
            "name": row[5]
        } for row in rows
    ]
