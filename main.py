# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()  # loads .env if running locally

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require', cursor_factory=RealDictCursor)

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
            lat FLOAT,
            lng FLOAT,
            color TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

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
async def post_location(request: Request):
    data = await request.json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO locations (name, city, state, country, lat, lng, color)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        data.get("name"),
        data.get("city"),
        data.get("state"),
        data.get("country"),
        data.get("lat"),
        data.get("lng"),
        data.get("color", "red")
    ))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}
