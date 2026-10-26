import sqlite3
import pandas as pd
import numpy as np
import os
import hashlib
import json
from dataset_profiler import profile_dataframe

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "astral.db"))
ZOMATO_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "zomato dataset", "zomato.csv"))
USER_UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "user_uploads"))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def clean_zomato_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # 1. Clean 'rate' column e.g. "4.1/5" -> 4.1
    def parse_rate(val):
        if pd.isna(val) or val in ['NEW', '-', '']:
            return None
        val_str = str(val).split('/')[0].strip()
        try:
            return float(val_str)
        except Exception:
            return None
            
    # 2. Clean 'approx_cost(for two people)' column e.g. "1,200" -> 1200.0
    def parse_cost(val):
        if pd.isna(val) or val in ['-', '']:
            return None
        val_str = str(val).replace(',', '').strip()
        try:
            return float(val_str)
        except Exception:
            return None

    # 3. Clean 'votes'
    def parse_votes(val):
        try:
            return int(val)
        except Exception:
            return 0

    df['rate_num'] = df['rate'].apply(parse_rate)
    df['cost_num'] = df['approx_cost(for two people)'].apply(parse_cost)
    df['votes_num'] = df['votes'].apply(parse_votes)
    
    return df

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(USER_UPLOADS_DIR, exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'Executive Manager',
        company TEXT DEFAULT 'ASTRAL Global Enterprise'
    )
    """)
    
    # 2. User Datasets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        row_count INTEGER,
        col_count INTEGER,
        table_name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 3. Dataset Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        profile_json TEXT NOT NULL,
        FOREIGN KEY (dataset_id) REFERENCES user_datasets (id)
    )
    """)

    conn.commit()

    # Seed Default Executive User if not exists
    cursor.execute("SELECT id FROM users WHERE email = 'admin@astral.ai'")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO users (email, name, password_hash, role, company)
        VALUES ('admin@astral.ai', 'Ritika Sharma', ?, 'Business Manager', 'ASTRAL Enterprise Solutions')
        """, (hash_password("astral2026"),))
        conn.commit()
        print("Default executive user created: admin@astral.ai / astral2026")

    # Ingest Zomato dataset if table does not exist or is empty
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='zomato_demo'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        if os.path.exists(ZOMATO_CSV_PATH):
            print(f"Ingesting Zomato dataset from {ZOMATO_CSV_PATH} into SQLite table 'zomato_demo'...")
            # Load CSV in chunks for memory efficiency
            chunk_list = []
            for chunk in pd.read_csv(ZOMATO_CSV_PATH, chunksize=10000, low_memory=False):
                cleaned_chunk = clean_zomato_data(chunk)
                chunk_list.append(cleaned_chunk)
                
            full_zomato_df = pd.concat(chunk_list, ignore_index=True)
            full_zomato_df.to_sql("zomato_demo", conn, if_exists="replace", index=False)
            
            # Create indexes for sub-10ms query execution
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_zomato_city ON zomato_demo (`listed_in(city)`)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_zomato_location ON zomato_demo (`location`)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_zomato_rate ON zomato_demo (`rate_num`)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_zomato_rest_type ON zomato_demo (`rest_type`)")
            
            conn.commit()
            print(f"Successfully seeded {len(full_zomato_df)} rows into 'zomato_demo' table!")
        else:
            print(f"Warning: Zomato CSV not found at {ZOMATO_CSV_PATH}")
    else:
        print("Zomato demo table 'zomato_demo' is ready.")

    conn.close()

def get_dataset_by_id(dataset_id: int, user_id: int = 1):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if dataset_id == 0 or dataset_id == "0" or str(dataset_id).lower() == "zomato":
        # Return Zomato DataFrame
        df = pd.read_sql_query("SELECT * FROM zomato_demo", conn)
        conn.close()
        prof = profile_dataframe(df, "Zomato Business Intelligence")
        return {
            "id": 0,
            "name": "Zomato Business Intelligence",
            "type": "demo",
            "df": df,
            "profile": prof
        }
        
    cursor.execute("SELECT * FROM user_datasets WHERE id = ? AND user_id = ?", (dataset_id, user_id))
    ds_row = cursor.fetchone()
    
    if not ds_row:
        conn.close()
        # Fallback to Zomato if dataset not found
        return get_dataset_by_id(0, user_id)
        
    table_name = ds_row['table_name']
    df = pd.read_sql_query(f"SELECT * FROM `{table_name}`", conn)
    
    cursor.execute("SELECT profile_json FROM dataset_profiles WHERE dataset_id = ?", (dataset_id,))
    prof_row = cursor.fetchone()
    conn.close()
    
    profile = json.loads(prof_row['profile_json']) if prof_row else profile_dataframe(df, ds_row['name'])
    
    return {
        "id": ds_row['id'],
        "name": ds_row['name'],
        "type": "user",
        "df": df,
        "profile": profile
    }

if __name__ == "__main__":
    init_db()
