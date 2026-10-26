import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from database import get_dataset_by_id

def detect_anomalies(dataset_id: int = 0, user_id: int = 1):
    ds_info = get_dataset_by_id(dataset_id, user_id)
    df = ds_info['df']
    profile = ds_info['profile']
    
    if len(df) == 0:
        return {"supported": False, "reason": "Dataset contains 0 rows."}
        
    if ds_info['type'] == 'demo' or dataset_id == 0:
        # ZOMATO ANOMALY DETECTION
        clean_df = df.dropna(subset=['cost_num', 'votes_num', 'rate_num']).copy()
        if len(clean_df) < 15:
            return {"supported": False, "reason": "Insufficient numerical columns for anomaly detection."}
            
        sample = clean_df.head(100).copy()
        X = sample[['cost_num', 'votes_num', 'rate_num']]
        
        model = IsolationForest(contamination=0.10, random_state=42)
        sample['anomaly'] = model.fit_predict(X)
        
        anomalies_df = sample[sample['anomaly'] == -1].head(6)
        anomalies = []
        
        for idx, row in anomalies_df.iterrows():
            rate = float(row['rate_num'])
            cost = float(row['cost_num'])
            votes = int(row['votes_num'])
            
            if rate >= 4.6 and votes > 1000:
                severity = "Positive"
                issue = "Exceptional rating and viral vote volume detected."
                impact = f"Rated {rate}/5 with {votes:,} customer votes."
            elif cost > 2000:
                severity = "High"
                issue = "Unusually high dining cost outlier."
                impact = f"Approx cost for two is ₹{int(cost)}."
            else:
                severity = "Medium"
                issue = "Discrepancy between price point and customer ratings."
                impact = f"Cost ₹{int(cost)} with {votes} total votes."
                
            anomalies.append({
                "date": str(row['location']),
                "day_of_week": str(row['name']),
                "revenue": cost,
                "orders": votes,
                "severity": severity,
                "issue": issue,
                "impact": impact
            })
            
        return {
            "supported": True,
            "model_used": "IsolationForest",
            "total_anomalies_found": len(anomalies),
            "anomalies": anomalies
        }
        
    else:
        # USER DATASET ANOMALY DETECTION
        numeric_cols = profile.get('numeric_cols', [])
        if not numeric_cols:
            return {
                "supported": False,
                "reason": "This anomaly detection model is unavailable for the selected dataset because no numerical columns were found."
            }
            
        sample = df.dropna(subset=numeric_cols[:3]).head(100).copy()
        if len(sample) < 5:
            return {"supported": False, "reason": "Insufficient non-null numerical records for isolation forest model."}
            
        X = sample[numeric_cols[:3]]
        model = IsolationForest(contamination=0.10, random_state=42)
        sample['anomaly'] = model.fit_predict(X)
        
        anomalies_df = sample[sample['anomaly'] == -1].head(5)
        anomalies = []
        
        entity_col = profile['semantic_mappings'].get('entity_name_col') or sample.columns[0]
        num_col = numeric_cols[0]
        
        for idx, row in anomalies_df.iterrows():
            val = float(row[num_col]) if pd.notnull(row[num_col]) else 0.0
            anomalies.append({
                "date": f"Record #{idx+1}",
                "day_of_week": str(row[entity_col]),
                "revenue": val,
                "orders": 1,
                "severity": "Medium",
                "issue": f"Outlier detected in field '{num_col}'.",
                "impact": f"Value {val} deviates significantly from expected statistical baseline."
            })
            
        return {
            "supported": True,
            "model_used": "IsolationForest",
            "total_anomalies_found": len(anomalies),
            "anomalies": anomalies
        }
