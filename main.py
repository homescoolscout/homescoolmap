# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
import os

app = FastAPI()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    city TEXT NOT NULL,
    state TEXT,
    country TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL
);
""")
conn.commit()

# Location schema
class Location(BaseModel):
    name: str
    city: str
    state: Optional[str]
    country: str
    lat: float
    lng: float

@app.get("/")
def read_root():
    return {"message": "Homescool Map API is running"}

@app.post("/locations")
def add_location(location: Location):
    try:
        cursor.execute("""
            INSERT INTO locations (name, city, state, country, lat, lng)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (location.name, location.city, location.state, location.country, location.lat, location.lng))
        conn.commit()
        return {"message": "Location added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/locations")
def get_locations():
    cursor.execute("SELECT name, city, state, country, lat, lng FROM locations;")
    rows = cursor.fetchall()
    return [
        {
            "name": row[0],
            "city": row[1],
            "state": row[2],
            "country": row[3],
            "lat": row[4],
            "lng": row[5]
        }
        for row in rows
    ]
