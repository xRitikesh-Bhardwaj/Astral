from fastapi import APIRouter, HTTPException, Depends
from schemas import LoginRequest, LoginResponse, ChangePasswordRequest, RegisterRequest
import sqlite3
import hashlib
import os

router = APIRouter(prefix="/api", tags=["Auth"])
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "astral.db"))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    hashed = hash_password(req.password)
    # Search by email OR username (name)
    cursor.execute(
        "SELECT * FROM users WHERE (email = ? OR name = ?) AND password_hash = ?", 
        (req.email, req.email, hashed)
    )
    user = cursor.fetchone()
    
    # Allow demo executive login with admin@astral.ai or admin
    if not user and (req.email in ["admin@astral.ai", "admin"]):
        cursor.execute("SELECT * FROM users WHERE email = 'admin@astral.ai'")
        user = cursor.fetchone()
        
    conn.close()
    
    if not user:
        if req.email in ["admin@astral.ai", "admin", "manager@astral.ai"]:
            return LoginResponse(
                status="success",
                token="astral_token_executive_2026",
                user={
                    "name": "Ritika Sharma",
                    "email": "ritika@astral.ai",
                    "role": "Business Manager",
                    "company": "ASTRAL Enterprise Solutions"
                }
            )
        raise HTTPException(status_code=401, detail="Invalid username/email or password.")
        
    return LoginResponse(
        status="success",
        token=f"astral_session_{user['id']}_2026",
        user={
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "company": user['company']
        }
    )

@router.post("/change-password")
def change_password(req: ChangePasswordRequest):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    old_hashed = hash_password(req.old_password)
    new_hashed = hash_password(req.new_password)
    
    # Check if user exists with old password
    cursor.execute(
        "SELECT * FROM users WHERE (email = ? OR name = ?) AND password_hash = ?",
        (req.email, req.email, old_hashed)
    )
    user = cursor.fetchone()
    
    # Special handling for default admin demo user
    if not user and (req.email in ["admin@astral.ai", "admin"]):
        cursor.execute("SELECT * FROM users WHERE email = 'admin@astral.ai'")
        user = cursor.fetchone()
        
    if not user:
        conn.close()
        raise HTTPException(status_code=400, detail="User not found or incorrect old password.")
        
    # Update password in database
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hashed, user['id']))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": "Password changed successfully! Please log in with your new password."
    }

@router.post("/register", response_model=LoginResponse)
def register(req: RegisterRequest):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (req.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
        
    hashed = hash_password(req.password)
    company_name = req.company or "ASTRAL Enterprise"
    
    cursor.execute(
        "INSERT INTO users (email, name, password_hash, role, company) VALUES (?, ?, ?, 'Business Manager', ?)",
        (req.email, req.name, hashed, company_name)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return LoginResponse(
        status="success",
        token=f"astral_session_{user_id}_2026",
        user={
            "id": user_id,
            "name": req.name,
            "email": req.email,
            "role": "Business Manager",
            "company": company_name
        }
    )

@router.get("/me")
def get_current_user():
    return {
        "name": "Ritika Sharma",
        "email": "ritika@astral.ai",
        "role": "Business Manager",
        "company": "ASTRAL Enterprise Solutions",
        "avatar": "RS"
    }

