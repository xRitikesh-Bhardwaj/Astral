from fastapi import APIRouter, Header, Query
from typing import Optional
from schemas import SimulationRequest
from database import get_dataset_by_id

router = APIRouter(prefix="/api/digital-twin", tags=["Digital Twin"])

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

@router.post("/simulate")
def simulate_scenario(
    req: SimulationRequest,
    x_user_id: Optional[str] = Header(None),
    x_dataset_id: Optional[str] = Header(None),
    dataset_id: Optional[int] = Query(None)
):
    user_id, ds_id = get_header_user_dataset_id(x_user_id, x_dataset_id, dataset_id)
    ds_info = get_dataset_by_id(ds_id, user_id)
    df = ds_info['df']

    if ds_info['type'] == 'demo' or ds_id == 0:
        base_revenue = float(len(df) * 550)  # ~₹2.84 Cr
        base_orders = int(df['votes_num'].sum()) if 'votes_num' in df else 50000
        base_profit = float(base_revenue * 0.25)
        base_customers = len(df)
        currency_label = "₹"
    else:
        profile = ds_info['profile']
        num_col = profile['semantic_mappings'].get('numeric_value_col')
        base_revenue = float(df[num_col].sum()) if num_col and num_col in df else float(len(df) * 1000)
        base_orders = len(df)
        base_profit = base_revenue * 0.20
        base_customers = profile['row_count']
        currency_label = ""

    # Calculate simulation factors
    sales_factor = 1.0 + (req.sales_growth / 100.0)
    customer_factor = 1.0 + (req.customer_growth / 100.0)
    discount_factor = 1.0 - (req.discount_rate / 100.0 * 0.3)
    mktg_roi_boost = (req.marketing_spend / 500000.0) * 0.02

    sim_revenue = max(0.0, base_revenue * sales_factor * discount_factor * (1.0 + mktg_roi_boost))
    sim_orders = int(max(0, base_orders * sales_factor * (1.0 + (req.order_volume / 100.0))))
    sim_customers = int(max(0, base_customers * customer_factor))

    raw_profit = sim_revenue * 0.25 * discount_factor - req.marketing_spend
    sim_profit = max(base_profit * 0.2, raw_profit)

    rev_diff_pct = round(((sim_revenue - base_revenue) / base_revenue) * 100, 1) if base_revenue > 0 else 0.0
    orders_diff_pct = round(((sim_orders - base_orders) / base_orders) * 100, 1) if base_orders > 0 else 0.0
    profit_diff_pct = round(((sim_profit - base_profit) / base_profit) * 100, 1) if base_profit > 0 else 0.0
    cust_diff_pct = round(((sim_customers - base_customers) / base_customers) * 100, 1) if base_customers > 0 else 0.0

    return {
        "status": "success",
        "dataset_name": ds_info['name'],
        "current_scenario": {
            "revenue": base_revenue,
            "formatted_revenue": f"{currency_label}{round(base_revenue/10000000, 2)} Cr" if base_revenue >= 10000000 else f"{currency_label}{round(base_revenue/100000, 1)} Lakhs",
            "orders": base_orders,
            "profit": base_profit,
            "formatted_profit": f"{currency_label}{round(base_profit/100000, 1)} Lakhs",
            "customers": base_customers
        },
        "simulated_scenario": {
            "revenue": round(sim_revenue, 2),
            "formatted_revenue": f"{currency_label}{round(sim_revenue/10000000, 2)} Cr" if sim_revenue >= 10000000 else f"{currency_label}{round(sim_revenue/100000, 1)} Lakhs",
            "orders": sim_orders,
            "profit": round(sim_profit, 2),
            "formatted_profit": f"{currency_label}{round(sim_profit/100000, 1)} Lakhs",
            "customers": sim_customers
        },
        "impact_analysis": {
            "revenue_change_pct": f"{'+' if rev_diff_pct >= 0 else ''}{rev_diff_pct}%",
            "orders_change_pct": f"{'+' if orders_diff_pct >= 0 else ''}{orders_diff_pct}%",
            "profit_change_pct": f"{'+' if profit_diff_pct >= 0 else ''}{profit_diff_pct}%",
            "customers_change_pct": f"{'+' if cust_diff_pct >= 0 else ''}{cust_diff_pct}%"
        },
        "recommendation": (
            f"Simulated strategy on dataset '{ds_info['name']}': Adjusting sales growth by {req.sales_growth}% "
            f"and discount rate by {req.discount_rate}% yields a net profit shift of {profit_diff_pct}%."
        )
    }
