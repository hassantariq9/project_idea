from sqlalchemy import create_engine, text
import pandas as pd
from config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL, echo=False)

# -----------------------------
# Initialize Tables
# -----------------------------

def init_db():

    with engine.begin() as conn:

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            email TEXT,
            role TEXT
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT,
            title TEXT,
            description TEXT,
            timestamp TEXT,
            status TEXT,
            similarity REAL,
            cluster INTEGER,
            comments TEXT
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            message TEXT,
            timestamp TEXT
        )
        """))

# -----------------------------
# Read Query
# -----------------------------

def read(query):
    return pd.read_sql(query, engine)

# -----------------------------
# Write DataFrame
# -----------------------------

def write(df, table):
    df.to_sql(table, engine, if_exists="append", index=False)

# -----------------------------
# Execute SQL (update/delete)
# -----------------------------

def execute(query, params=None):

    with engine.begin() as conn:

        if params:
            conn.execute(text(query), params)
        else:
            conn.execute(text(query))
