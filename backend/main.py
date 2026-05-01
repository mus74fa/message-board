from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

@app.on_event("startup")
def startup():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

class MessageInput(BaseModel):
    name: str
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/messages")
def get_messages():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, message, created_at FROM messages ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "message": r[2], "created_at": str(r[3])}
        for r in rows
    ]

@app.post("/messages")
def post_message(data: MessageInput):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (name, message) VALUES (%s, %s)",
        (data.name, data.message)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "saved"}