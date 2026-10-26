from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Query
import pandas as pd
import numpy as np
import os
import json
import sqlite3
from typing import Optional, List, Dict, Any
from database import get_db_connection, DB_PATH, USER_UPLOADS_DIR
from dataset_profiler import profile_dataframe

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    try:
        if x_user_id:
            return int(x_user_id)
    except Exception:
        pass
    return 1 # Default demo user ID

@router.get("")
def list_datasets(x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(x_user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Always include Zomato Demo
    cursor.execute("SELECT COUNT(*) FROM zomato_demo")
    zomato_count_row = cursor.fetchone()
    zomato_rows = zomato_count_row[0] if zomato_count_row else 51717
    
    datasets = [{
        "id": 0,
        "name": "Zomato Business Intelligence",
        "type": "demo",
        "row_count": zomato_rows,
        "col_count": 17,
        "description": "Preloaded Zomato Bangalore restaurant & business dataset.",
        "created_at": "Preloaded Demo"
    }]
    
    # 2. Fetch user's uploaded datasets
    cursor.execute("SELECT id, name, filename, row_count, col_count, created_at FROM user_datasets WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        datasets.append({
            "id": row['id'],
            "name": row['name'],
            "type": "user",
            "filename": row['filename'],
            "row_count": row['row_count'],
            "col_count": row['col_count'],
            "description": f"User Uploaded Dataset ({row['row_count']} rows)",
            "created_at": row['created_at']
        })
        
    return {"status": "success", "datasets": datasets}

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    x_user_id: Optional[str] = Header(None)
):
    user_id = get_current_user_id(x_user_id)
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or Excel (.xlsx/.xls) file.")
        
    user_dir = os.path.join(USER_UPLOADS_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    saved_path = os.path.join(user_dir, filename)
    
    # Read file content
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Dataset file is empty.")
        
    with open(saved_path, "wb") as f:
        f.write(contents)
        
    try:
        if ext == ".csv":
            df = pd.read_csv(saved_path, low_memory=False)
        else:
            df = pd.read_excel(saved_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to parse structured data from file: {str(e)}")
        
    if len(df) == 0:
        raise HTTPException(status_code=400, detail="Dataset contains 0 rows of data.")
        
    if len(df.columns) == 0:
        raise HTTPException(status_code=400, detail="Dataset contains no usable columns.")
        
    # Standardize column names for SQL safety
    clean_cols = [str(c).strip().replace(" ", "_").replace(".", "_") for c in df.columns]
    df.columns = clean_cols
    
    # Build dataset profile
    dataset_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
    profile = profile_dataframe(df, dataset_name)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert metadata into user_datasets
    dummy_table = f"user_ds_temp_{user_id}"
    cursor.execute("""
    INSERT INTO user_datasets (user_id, name, filename, file_path, row_count, col_count, table_name)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, dataset_name, filename, saved_path, len(df), len(df.columns), dummy_table))
    
    dataset_id = cursor.lastrowid
    real_table = f"user_dataset_{dataset_id}"
    
    # Update table_name
    cursor.execute("UPDATE user_datasets SET table_name = ? WHERE id = ?", (real_table, dataset_id))
    
    # Save dataframe to SQLite table
    df.to_sql(real_table, conn, if_exists="replace", index=False)
    
    # Save profile JSON
    cursor.execute("""
    INSERT INTO dataset_profiles (dataset_id, profile_json)
    VALUES (?, ?)
    """, (dataset_id, json.dumps(profile)))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"Dataset '{dataset_name}' successfully uploaded and analyzed!",
        "dataset_id": dataset_id,
        "name": dataset_name,
        "filename": filename,
        "row_count": len(df),
        "col_count": len(df.columns),
        "profile": profile
    }

@router.get("/{dataset_id}/profile")
def get_dataset_profile(dataset_id: int, x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(x_user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if dataset_id == 0:
        cursor.execute("SELECT * FROM zomato_demo")
        df = pd.read_sql_query("SELECT * FROM zomato_demo", conn)
        conn.close()
        prof = profile_dataframe(df, "Zomato Business Intelligence")
        return {"status": "success", "dataset_id": 0, "profile": prof}
        
    cursor.execute("SELECT * FROM user_datasets WHERE id = ? AND user_id = ?", (dataset_id, user_id))
    ds = cursor.fetchone()
    if not ds:
        conn.close()
        raise HTTPException(status_code=404, detail="Dataset not found or access denied.")
        
    cursor.execute("SELECT profile_json FROM dataset_profiles WHERE dataset_id = ?", (dataset_id,))
    prof_row = cursor.fetchone()
    conn.close()
    
    if prof_row:
        profile = json.loads(prof_row['profile_json'])
    else:
        profile = {}
        
    return {"status": "success", "dataset_id": dataset_id, "name": ds['name'], "profile": profile}

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(x_user_id)
    if dataset_id == 0:
        raise HTTPException(status_code=400, detail="Cannot delete default Zomato demo dataset.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_datasets WHERE id = ? AND user_id = ?", (dataset_id, user_id))
    ds = cursor.fetchone()
    if not ds:
        conn.close()
        raise HTTPException(status_code=404, detail="Dataset not found or access denied.")
        
    table_name = ds['table_name']
    file_path = ds['file_path']
    
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
    cursor.execute("DELETE FROM dataset_profiles WHERE dataset_id = ?", (dataset_id,))
    cursor.execute("DELETE FROM user_datasets WHERE id = ?", (dataset_id,))
    
    conn.commit()
    conn.close()
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
            
    return {"status": "success", "message": f"Dataset '{ds['name']}' deleted successfully."}
