from fastapi import APIRouter, Header, Query
from typing import Optional
from ml.revenue_prediction import predict_revenue
from ml.churn_prediction import predict_churn
from ml.anomaly_detection import detect_anomalies

router = APIRouter(prefix="/api", tags=["Predictions"])

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

@router.get("/predictions/revenue")
def get_revenue_predictions(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    return predict_revenue(ds_id, user_id)

@router.get("/predictions/churn")
def get_churn_predictions(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    return predict_churn(ds_id, user_id)

@router.get("/anomalies")
def get_anomalies(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    return detect_anomalies(ds_id, user_id)
