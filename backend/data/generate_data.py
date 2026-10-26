import csv
import random
from datetime import datetime, timedelta

def generate_csv():
    start_date = datetime(2025, 8, 12)
    rows = []
    categories = ["Electronics", "Enterprise Software", "Cloud Services", "Hardware", "Consulting"]
    
    # Base parameters
    base_revenue = 3000000  # ~30 Lakhs per day base
    
    for i in range(365):
        curr_date = start_date + timedelta(days=i)
        date_str = curr_date.strftime("%Y-%m-%d")
        day_of_week = curr_date.strftime("%A")
        is_weekend = day_of_week in ["Saturday", "Sunday"]
        
        # Seasonality factor
        weekend_mult = 0.82 if is_weekend else 1.05
        seasonal_mult = 1.0 + (i / 365.0) * 0.25 + random.uniform(-0.08, 0.08)
        
        revenue = round(base_revenue * weekend_mult * seasonal_mult, 2)
        orders = int(revenue / random.uniform(2500, 3200))
        customers_active = int(orders * random.uniform(0.7, 0.85))
        new_customers = random.randint(15, 65)
        profit = round(revenue * random.uniform(0.24, 0.28), 2)
        
        # Category breakdown in INR
        elec_rev = round(revenue * 0.38, 2)
        sw_rev = round(revenue * 0.26, 2)
        cloud_rev = round(revenue * 0.20, 2)
        hw_rev = round(revenue * 0.10, 2)
        cons_rev = round(revenue * 0.06, 2)
        
        rows.append([
            date_str, day_of_week, revenue, orders, customers_active, new_customers, profit,
            elec_rev, sw_rev, cloud_rev, hw_rev, cons_rev
        ])

    headers = [
        "date", "day_of_week", "revenue", "orders", "customers_active", "new_customers", "profit",
        "cat_electronics", "cat_software", "cat_cloud", "cat_hardware", "cat_consulting"
    ]

    with open("c:/Users/hp/Desktop/Astral/backend/data/business_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print("CSV generated successfully!")

if __name__ == "__main__":
    generate_csv()
