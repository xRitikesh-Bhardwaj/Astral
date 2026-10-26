from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class LoginRequest(BaseModel):
    email: str  # Email or Username
    password: str

class LoginResponse(BaseModel):
    status: str
    token: str
    user: Dict[str, Any]

class ChangePasswordRequest(BaseModel):
    email: str  # Email or Username
    old_password: str
    new_password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    company: Optional[str] = "ASTRAL Enterprise"

class AIQueryRequest(BaseModel):
    question: str

class SimulationRequest(BaseModel):
    sales_growth: float = 0.0
    customer_growth: float = 0.0
    discount_rate: float = 0.0
    marketing_spend: float = 0.0
    order_volume: float = 0.0

