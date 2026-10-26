import pandas as pd
import numpy as np
from typing import Dict, Any, List

def profile_dataframe(df: pd.DataFrame, dataset_name: str = "") -> Dict[str, Any]:
    row_count = len(df)
    col_count = len(df.columns)
    
    if row_count == 0:
        return {
            "dataset_name": dataset_name,
            "row_count": 0,
            "col_count": col_count,
            "error": "Dataset contains 0 rows."
        }

    total_cells = row_count * col_count
    null_cells = int(df.isnull().sum().sum())
    null_pct = round((null_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0
    duplicate_rows = int(df.duplicated().sum())
    
    columns_info = []
    semantic_mappings = {
        "entity_name_col": None,
        "category_col": None,
        "location_col": None,
        "rating_col": None,
        "numeric_value_col": None,
        "quantity_col": None,
        "date_col": None
    }
    
    numeric_cols = []
    categorical_cols = []
    date_cols = []
    
    for col in df.columns:
        col_str = str(col)
        col_lower = col_str.lower().strip()
        series = df[col]
        
        # Determine column data type
        is_numeric = pd.api.types.is_numeric_dtype(series)
        is_datetime = pd.api.types.is_datetime64_any_dtype(series)
        
        # Try datetime conversion if string and column name sounds date-like
        if not is_datetime and any(d in col_lower for d in ['date', 'time', 'timestamp', 'created', 'year', 'month']):
            try:
                converted = pd.to_datetime(series, errors='coerce')
                if converted.notnull().sum() > 0.5 * row_count:
                    is_datetime = True
            except Exception:
                pass
                
        unique_cnt = int(series.nunique(dropna=True))
        null_cnt = int(series.isnull().sum())
        
        col_type = "numeric" if is_numeric else "date" if is_datetime else "categorical"
        if col_type == "numeric":
            numeric_cols.append(col_str)
        elif col_type == "date":
            date_cols.append(col_str)
        else:
            categorical_cols.append(col_str)
            
        sample_vals = [str(x) for x in series.dropna().unique()[:3]]
        
        columns_info.append({
            "name": col_str,
            "type": col_type,
            "null_count": null_cnt,
            "unique_count": unique_cnt,
            "sample_values": sample_vals
        })
        
        # Semantic mapping heuristics
        if not semantic_mappings["entity_name_col"]:
            if any(k in col_lower for k in ['name', 'title', 'restaurant', 'product', 'item', 'customer', 'company', 'client']):
                semantic_mappings["entity_name_col"] = col_str
                
        if not semantic_mappings["category_col"]:
            if any(k in col_lower for k in ['cuisine', 'category', 'rest_type', 'type', 'group', 'segment', 'genre']):
                semantic_mappings["category_col"] = col_str

        if not semantic_mappings["location_col"]:
            if any(k in col_lower for k in ['location', 'city', 'address', 'region', 'state', 'country', 'listed_in(city)']):
                semantic_mappings["location_col"] = col_str

        if not semantic_mappings["rating_col"]:
            if any(k in col_lower for k in ['rate', 'rating', 'score', 'stars']):
                semantic_mappings["rating_col"] = col_str

        if not semantic_mappings["numeric_value_col"]:
            if any(k in col_lower for k in ['price', 'cost', 'revenue', 'amount', 'sales', 'spend', 'approx_cost']):
                semantic_mappings["numeric_value_col"] = col_str

        if not semantic_mappings["quantity_col"]:
            if any(k in col_lower for k in ['vote', 'votes', 'quantity', 'order', 'orders', 'units', 'volume', 'count']):
                semantic_mappings["quantity_col"] = col_str

        if not semantic_mappings["date_col"]:
            if is_datetime or any(k in col_lower for k in ['date', 'time', 'created', 'order_date']):
                semantic_mappings["date_col"] = col_str

    # Fallbacks if semantic mapping missed anything
    if not semantic_mappings["entity_name_col"] and categorical_cols:
        semantic_mappings["entity_name_col"] = categorical_cols[0]
    if not semantic_mappings["category_col"] and len(categorical_cols) > 1:
        semantic_mappings["category_col"] = categorical_cols[1]
    if not semantic_mappings["numeric_value_col"] and numeric_cols:
        semantic_mappings["numeric_value_col"] = numeric_cols[0]
    if not semantic_mappings["quantity_col"] and len(numeric_cols) > 1:
        semantic_mappings["quantity_col"] = numeric_cols[1]

    return {
        "dataset_name": dataset_name,
        "row_count": row_count,
        "col_count": col_count,
        "total_cells": total_cells,
        "null_cells": null_cells,
        "null_percentage": null_pct,
        "duplicate_rows": duplicate_rows,
        "numeric_cols_count": len(numeric_cols),
        "categorical_cols_count": len(categorical_cols),
        "date_cols_count": len(date_cols),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "date_cols": date_cols,
        "columns": columns_info,
        "semantic_mappings": semantic_mappings
    }
