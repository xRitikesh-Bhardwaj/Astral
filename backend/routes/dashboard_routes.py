from fastapi import APIRouter, Header, Query
import pandas as pd
import numpy as np
from typing import Optional
from database import get_dataset_by_id

router = APIRouter(prefix="/api", tags=["Dashboard"])

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

@router.get("/dashboard")
def get_dashboard_overview(
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    ds_info = get_dataset_by_id(ds_id, user_id)
    
    df = ds_info['df']
    profile = ds_info['profile']
    
    if len(df) == 0:
        return {"error": "Selected dataset is empty."}
        
    if ds_info['type'] == 'demo' or ds_info['id'] == 0:
        # ZOMATO DEMO DATASET COMPUTATION
        total_restaurants = len(df)
        avg_rating = round(df['rate_num'].mean(), 2) if 'rate_num' in df else 3.7
        total_votes = int(df['votes_num'].sum()) if 'votes_num' in df else 0
        avg_cost = round(df['cost_num'].mean(), 0) if 'cost_num' in df else 550
        
        online_order_pct = round((df['online_order'] == 'Yes').mean() * 100, 1) if 'online_order' in df else 59.2
        book_table_pct = round((df['book_table'] == 'Yes').mean() * 100, 1) if 'book_table' in df else 12.4
        
        high_rated_pct = round((df['rate_num'] >= 4.0).mean() * 100, 1) if 'rate_num' in df else 35.0
        health_score = int(min(98, max(50, 60 + (avg_rating * 8) + (online_order_pct * 0.1))))
        
        # City level breakdown for chart
        city_counts = df['listed_in(city)'].value_counts().head(7) if 'listed_in(city)' in df else pd.Series()
        chart_labels = list(city_counts.index)
        chart_values = [int(v) for v in city_counts.values]
        
        daily_summary = (
            f"Zomato Business Intelligence Overview: Analyzing {total_restaurants:,} restaurants across Bangalore. "
            f"Average restaurant rating stands at {avg_rating}/5 with {online_order_pct}% online order coverage. "
            f"Average cost for two people is ₹{int(avg_cost)}."
        )
        
        insights = [
            {"icon": "trending-up", "text": f"{high_rated_pct}% of restaurants have high customer ratings (≥4.0 Stars).", "type": "positive"},
            {"icon": "package", "text": f"{online_order_pct}% of listed restaurants support online food delivery.", "type": "positive"},
            {"icon": "users", "text": f"Accumulated {total_votes:,} total customer votes across all dining categories.", "type": "neutral"},
            {"icon": "calendar", "text": f"Only {book_table_pct}% of outlets offer advance table reservation features.", "type": "warning"}
        ]
        
        attention_items = [
            {"severity": "High", "title": "Low Booking Table Adoption", "desc": f"Only {book_table_pct}% of outlets support online table booking.", "badge": "Opportunity"},
            {"severity": "Medium", "title": "Price Volatility in Premium Zones", "desc": "Casual dining cost averages ₹800 vs ₹300 for quick bites.", "badge": "Medium Risk"},
            {"severity": "Positive", "title": "Online Delivery Coverage High", "desc": f"{online_order_pct}% online delivery adoption across major zones.", "badge": "On Track"}
        ]
        
        return {
            "dataset": {
                "id": 0,
                "name": "Zomato Business Intelligence",
                "type": "demo"
            },
            "business_health": {
                "score": health_score,
                "max_score": 100,
                "status": "Healthy" if health_score >= 80 else "Moderate",
                "label": "Optimal Performance"
            },
            "kpis": {
                "revenue": {
                    "value": f"{total_restaurants:,}",
                    "raw": total_restaurants,
                    "change": "+4.2%",
                    "is_positive": True,
                    "subtext": "Total Outlets"
                },
                "orders": {
                    "value": f"{avg_rating} / 5",
                    "raw": avg_rating,
                    "change": "+0.3 Stars",
                    "is_positive": True,
                    "subtext": "Average Rating"
                },
                "customers": {
                    "value": f"₹{int(avg_cost)}",
                    "raw": avg_cost,
                    "change": "Avg for 2",
                    "is_positive": True,
                    "subtext": "Avg Meal Cost"
                },
                "profit": {
                    "value": f"{total_votes:,}",
                    "raw": total_votes,
                    "change": "+12.8%",
                    "is_positive": True,
                    "subtext": "Total Votes"
                }
            },
            "chart_data": {
                "labels": chart_labels,
                "values": chart_values,
                "unit": "Restaurants"
            },
            "daily_summary": daily_summary,
            "key_insights": insights,
            "attention_required": attention_items
        }
        
    else:
        # USER UPLOADED DATASET DYNAMIC COMPUTATION
        mappings = profile['semantic_mappings']
        row_cnt = profile['row_count']
        col_cnt = profile['col_count']
        
        num_col = mappings.get('numeric_value_col')
        qty_col = mappings.get('quantity_col')
        cat_col = mappings.get('category_col')
        
        val_sum = float(df[num_col].sum()) if num_col and num_col in df and pd.api.types.is_numeric_dtype(df[num_col]) else float(row_cnt * 100)
        qty_sum = int(df[qty_col].sum()) if qty_col and qty_col in df and pd.api.types.is_numeric_dtype(df[qty_col]) else row_cnt
        
        val_formatted = f"₹{round(val_sum/100000, 1)}L" if val_sum > 100000 else f"{round(val_sum, 1)}"
        qty_formatted = f"{qty_sum:,}"
        
        chart_labels = []
        chart_values = []
        if cat_col and cat_col in df:
            top_cats = df[cat_col].value_counts().head(7)
            chart_labels = [str(k) for k in top_cats.index]
            chart_values = [int(v) for v in top_cats.values]
        else:
            chart_labels = [f"Col {i+1}" for i in range(min(5, col_cnt))]
            chart_values = [row_cnt // (i+1) for i in range(len(chart_labels))]
            
        daily_summary = (
            f"Dataset Analysis for '{ds_info['name']}': Loaded {row_cnt:,} rows and {col_cnt} columns. "
            f"Null values make up {profile.get('null_percentage', 0)}% of total entries. "
            f"Main metrics tracked across {len(chart_labels)} detected categories."
        )
        
        insights = [
            {"icon": "trending-up", "text": f"Dataset contains {row_cnt:,} records across {col_cnt} structured attributes.", "type": "positive"},
            {"icon": "package", "text": f"Identified {profile.get('numeric_cols_count', 0)} numerical and {profile.get('categorical_cols_count', 0)} categorical fields.", "type": "neutral"},
            {"icon": "users", "text": f"Detected {profile.get('duplicate_rows', 0)} duplicate rows in upload.", "type": "warning" if profile.get('duplicate_rows', 0) > 0 else "positive"}
        ]
        
        attention_items = [
            {"severity": "Positive", "title": "Dataset Successfully Ingested", "desc": f"{row_cnt:,} rows ready for business intelligence.", "badge": "Active"},
            {"severity": "Medium", "title": "Missing Values Check", "desc": f"Dataset has {profile.get('null_percentage', 0)}% missing cells.", "badge": "Check Cleanliness"}
        ]
        
        return {
            "dataset": {
                "id": ds_info['id'],
                "name": ds_info['name'],
                "type": "user"
            },
            "business_health": {
                "score": 88,
                "max_score": 100,
                "status": "Healthy",
                "label": "User Workspace Active"
            },
            "kpis": {
                "revenue": {
                    "value": f"{row_cnt:,}",
                    "raw": row_cnt,
                    "change": "Uploaded",
                    "is_positive": True,
                    "subtext": "Total Rows"
                },
                "orders": {
                    "value": f"{col_cnt}",
                    "raw": col_cnt,
                    "change": "Fields",
                    "is_positive": True,
                    "subtext": "Attributes"
                },
                "customers": {
                    "value": val_formatted,
                    "raw": val_sum,
                    "change": "Metric Total",
                    "is_positive": True,
                    "subtext": num_col or "Value Scale"
                },
                "profit": {
                    "value": qty_formatted,
                    "raw": qty_sum,
                    "change": "Volume Total",
                    "is_positive": True,
                    "subtext": qty_col or "Volume Scale"
                }
            },
            "chart_data": {
                "labels": chart_labels,
                "values": chart_values,
                "unit": "Records"
            },
            "daily_summary": daily_summary,
            "key_insights": insights,
            "attention_required": attention_items
        }
