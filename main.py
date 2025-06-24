# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# CORS for frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to your Wix site if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Location(BaseModel):
    name: str
    city: str
    state: str
    country: str
    lat: float
    lng: float

# DB Connection
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Create table on startup (if not exists)
@app.on_event("startup")
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            name TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            lat DOUBLE PRECISION,
            lng DOUBLE PRECISION
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Routes
@app.get("/locations")
def get_locations():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM locations;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.post("/locations")
def add_location(loc: Location):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO locations (name, city, state, country, lat, lng)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (loc.name, loc.city, loc.state, loc.country, loc.lat, loc.lng))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Location added successfully"}
