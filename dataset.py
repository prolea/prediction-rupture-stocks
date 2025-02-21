import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

num_products = 50
num_days = 30

categories = ["Électronique", "Vêtements", "Alimentation", "Beauté", "Sport"]
products = [
    {
        "product_id": i,
        "product_name": fake.word().capitalize(),
        "category": random.choice(categories),
        "price": round(random.uniform(5,500), 2),
        "initial_stock":random.randint(20, 200)
    }
    for i in range(1, num_products + 1)
]

products_df = pd.DataFrame(products)

start_date = datetime.today() - timedelta(days=num_days)
date_range = [start_date + timedelta(days=i) for i in range(num_days)]


sales_data = []
for day in date_range:
    for product in products:
        units_sold = random.randint(0,10)
        is_promo = random.choice([0,1]) if random.random() < 0.2 else 0

        sales_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "product_id": product["product_id"],
            "stock_quantity": max(product["initial_stock"] - units_sold, 0),  # Mise à jour du stock
            "units_sold": units_sold,
            "is_promotion": is_promo,
            "weekday": day.strftime("%A"),  
            "season": "Hiver" if day.month in [12, 1, 2] else "Printemps" if day.month in [3, 4, 5] else "Été" if day.month in [6, 7, 8] else "Automne"
        })
        
        product["initial_stock"] -= units_sold

sales_df = pd.DataFrame(sales_data)

final_df = sales_df.merge(products_df, on="product_id", how="left")

print(final_df.head())

final_df.to_csv("sales_data.csv", index=False)