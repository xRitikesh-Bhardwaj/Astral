from fastapi import APIRouter, Header, Query
from fastapi.responses import Response
from typing import Optional
from reports.report_generator import generate_report, export_report_csv

router = APIRouter(prefix="/api/reports", tags=["Reports"])

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

@router.get("/daily")
def get_daily_report(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    return generate_report("daily", ds_id, user_id)

@router.get("/weekly")
def get_weekly_report(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    return generate_report("weekly", ds_id, user_id)

@router.get("/monthly")
def get_monthly_report(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    return generate_report("monthly", ds_id, user_id)

@router.get("/export-csv")
def download_csv_report(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    csv_data = export_report_csv(ds_id, user_id)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ASTRAL_Business_Report.csv"}
    )
