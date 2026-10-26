from fastapi import APIRouter, Header, Query
from typing import Optional
from schemas import AIQueryRequest
from ai.assistant import assistant_instance

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])

def get_header_user_dataset_id(x_user_id: Optional[str], x_dataset_id: Optional[str], query_dataset_id: Optional[int]):
    try:
        user_id = int(x_user_id) if x_user_id else 1
    except Exception:
        user_id = 1
        
    ds_id = 0
    if query_dataset_id is not None:
        ds_id = query_dataset_id
    elif x_dataset_id is not None:
        try:
            ds_id = int(x_dataset_id)
        except Exception:
            ds_id = 0
            
    return user_id, ds_id

@router.post("/ask")
def ask_ai(
    req: AIQueryRequest,
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    response = assistant_instance.answer_question(req.question, ds_id, user_id)
    return response
