from fastapi import APIRouter, Header, Query
import pandas as pd
import numpy as np
from typing import Optional
from database import get_dataset_by_id

router = APIRouter(prefix="/api", tags=["Analytics"])

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

@router.get("/analytics")
def get_analytics(
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
        # ZOMATO DEMO ANALYTICS
        
        # 1. Cuisines Distribution (Splitting multi-cuisine strings)
        cuisines_series = df['cuisines'].dropna().apply(lambda x: [c.strip() for c in str(x).split(',')])
        all_cuisines = [c for sublist in cuisines_series for c in sublist]
        cuisine_counts = pd.Series(all_cuisines).value_counts().head(6)
        cat_totals = {k: int(v) for k, v in cuisine_counts.items()}
        
        # 2. City Distribution
        city_counts = df['listed_in(city)'].value_counts().head(7) if 'listed_in(city)' in df else pd.Series()
        city_dates = list(city_counts.index)
        city_values = [int(v) for v in city_counts.values]
        
        # 3. Top Rated Restaurants
        top_df = df.sort_values(by=['votes_num', 'rate_num'], ascending=False).drop_duplicates(subset=['name']).head(8)
        top_products = []
        for _, row in top_df.iterrows():
            top_products.append({
                "name": str(row['name']),
                "category": str(row['cuisines']) if pd.notnull(row['cuisines']) else "Casual Dining",
                "sales_count": int(row['votes_num']) if pd.notnull(row['votes_num']) else 0,
                "revenue_generated": float(row['cost_num']) if pd.notnull(row['cost_num']) else 500.0,
                "growth_rate": round(float(row['rate_num']), 1) if pd.notnull(row['rate_num']) else 4.0
            })
            
        # 4. Rating Distribution
        rating_dist = {
            "4.5+ Stars": int((df['rate_num'] >= 4.5).sum()),
            "4.0 - 4.4 Stars": int(((df['rate_num'] >= 4.0) & (df['rate_num'] < 4.5)).sum()),
            "3.5 - 3.9 Stars": int(((df['rate_num'] >= 3.5) & (df['rate_num'] < 4.0)).sum()),
            "Below 3.5 Stars": int((df['rate_num'] < 3.5).sum())
        }

        return {
            "dataset_name": "Zomato Business Intelligence",
            "revenue_trend": {
                "labels": city_dates,
                "values": city_values,
                "title": "Restaurants by Zone / City"
            },
            "order_trend": {
                "labels": list(rating_dist.keys()),
                "values": list(rating_dist.values()),
                "title": "Rating Breakdown"
            },
            "customer_trend": {
                "labels": ["Online Order", "No Delivery"],
                "values": [int((df['online_order'] == 'Yes').sum()), int((df['online_order'] == 'No').sum())],
                "title": "Delivery Options"
            },
            "category_distribution": cat_totals,
            "top_products": top_products
        }
        
    else:
        # USER DATASET ANALYTICS
        mappings = profile['semantic_mappings']
        cat_col = mappings.get('category_col')
        entity_col = mappings.get('entity_name_col')
        num_col = mappings.get('numeric_value_col')
        qty_col = mappings.get('quantity_col')
        
        # Category totals
        cat_totals = {}
        if cat_col and cat_col in df:
            top_cats = df[cat_col].value_counts().head(6)
            cat_totals = {str(k): int(v) for k, v in top_cats.items()}
        else:
            cat_totals = {f"Col {i+1}": (i+1)*10 for i in range(5)}
            
        # Top Entities
        top_products = []
        if entity_col and entity_col in df:
            sort_by = num_col if num_col and num_col in df and pd.api.types.is_numeric_dtype(df[num_col]) else None
            if sort_by:
                top_df = df.sort_values(by=sort_by, ascending=False).head(8)
            else:
                top_df = df.head(8)
                
            for _, row in top_df.iterrows():
                val = float(row[num_col]) if num_col and num_col in df and pd.notnull(row[num_col]) else 100.0
                qty = int(row[qty_col]) if qty_col and qty_col in df and pd.notnull(row[qty_col]) else 1
                top_products.append({
                    "name": str(row[entity_col]),
                    "category": str(row[cat_col]) if cat_col and cat_col in df and pd.notnull(row[cat_col]) else "General",
                    "sales_count": qty,
                    "revenue_generated": val,
                    "growth_rate": 12.5
                })

        labels = list(cat_totals.keys())
        values = list(cat_totals.values())
        
        return {
            "dataset_name": ds_info['name'],
            "revenue_trend": {
                "labels": labels,
                "values": values,
                "title": f"Distribution by {cat_col or 'Category'}"
            },
            "order_trend": {
                "labels": labels,
                "values": [v * 2 for v in values],
                "title": "Volume Trends"
            },
            "customer_trend": {
                "labels": ["Active Records", "Null/Incomplete"],
                "values": [profile['row_count'] - profile['null_cells'], profile['null_cells']],
                "title": "Data Cleanliness"
            },
            "category_distribution": cat_totals,
            "top_products": top_products
        }
