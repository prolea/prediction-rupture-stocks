import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

fake = Faker()

num_products = 50
num_days = 30

# Génération  des produits
categories = ["Électronique", "Vêtements", "Alimentation", "Beauté", "Sport"]
products = [
    {
        "product_id": i,
        "product_name": fake.word().capitalize(),
        "category": random.choice(categories),
        "price": round(random.uniform(5,500), 2)
    }
    for i in range(1, num_products + 1)
]

products_df = pd.DataFrame(products)

# Ajout du type de produit
product_types = ["normal"] * 25 + ["bestseller"] * 15 + ["niche"] * 10 #permet d'obtenir exactement 50% de produits normaux, 30% de bestseller et 20% de niche.
random.shuffle(product_types) # Mélange la distribution des types

products_df["product_type"] = product_types[:len(products_df)]

# Attribution du stock initial en fonction du type de produit
def assign_stock(product_type):
    if product_type == "bestseller":
        return random.randint(100,200)
    elif product_type == "niche":
        return random.randint(20,80)
    else: #normal
        return random.randint(50,150)

#application de la fonction à chaque ligne
products_df["initial_stock"] = products_df["product_type"].apply(assign_stock)

# Génération des ventes
start_date = datetime.today() - timedelta(days=num_days)
date_range = [start_date + timedelta(days=i) for i in range(num_days)]


sales_data = []
for day in date_range:
    for _, product in products_df.iterrows():
        # Attribution des ventes en fonction du type
        if product["product_type"] == "bestseller":
            units_sold = random.randint(5,15)
        elif product["product_type"] == "niche":
            units_sold = random.randint(0,5)
        else : #normal
            units_sold = random.randint(1,10)

        is_promo = random.choice([0,1]) if random.random() < 0.2 else 0

        # Enregistrement des ventes
        sales_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "product_id": product["product_id"],
            "units_sold": units_sold,
            "is_promotion": is_promo,
            "weekday": day.strftime("%A"),  
            "season": "Hiver" if day.month in [12, 1, 2] else "Printemps" if day.month in [3, 4, 5] else "Été" if day.month in [6, 7, 8] else "Automne"
        })

sales_df = pd.DataFrame(sales_data)
sales_df["date"] = pd.to_datetime(sales_df["date"])

sales_df = sales_df.merge(products_df[["product_id", "initial_stock"]], on="product_id", how="left")

sales_df["cumulative_sales"] = sales_df.groupby("product_id")["units_sold"].cumsum()
sales_df["remaining_stock"] = sales_df["initial_stock"] - sales_df["cumulative_sales"]
sales_df["remaining_stock"] = sales_df["remaining_stock"].clip(lower=0) # Évite les stocks négatifs

#Regroupement des ventes par type de produit
sales_by_type = sales_df.merge(products_df[["product_id", "product_type"]], on="product_id", how="left")
sales_by_type = sales_by_type.groupby("product_type")["units_sold"].sum().reset_index()

# Graphique comparaison des ventes par type de produit
plt.figure(figsize=(8,5))
sns.barplot(x="product_type", y="units_sold", data=sales_by_type, palette=["royalblue", "orange", "green"])

plt.title("Comparaison des ventes par type de produit")
plt.xlabel("Type de produit")
plt.ylabel("Nombre total d'unités vendues")
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Histogramme du stock avec KDE (distribution estimée)
plt.figure(figsize=(8,5))
sns.histplot(sales_df["remaining_stock"], bins=20, kde=True, color="royalblue")
plt.title("Répartition des stocks des produits")
plt.xlabel("Quantité en stock")
plt.ylabel("Nombre de produits")

# Courbe de tendance des ventes (sur 14 jours)
daily_sales = sales_df.groupby("date")["units_sold"].sum().reset_index()
daily_sales["moving_avg_14"] = daily_sales["units_sold"].rolling(window=14, min_periods=1).mean()

print(daily_sales.head())

plt.figure(figsize=(12,6))
sns.lineplot(x="date", y="units_sold", data=daily_sales, label="Ventes journalières", color="royalblue")
sns.lineplot(x="date", y="moving_avg_14", data=daily_sales, label="Moyenne mobile (14 jours)", color="green")

plt.title("Évolution des ventes journalières avec lissage sur 14 jours")
plt.xlabel("Date")
plt.ylabel("Nombre d'unités vendues")
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)

# relation entre le stock et les ventes
plt.figure(figsize=(10,5))
sns.scatterplot(x="date", y="remaining_stock", data=sales_df, alpha=0.5, color="royalblue")

plt.title("Évolution du stock restant")
plt.xlabel("Date")
plt.ylabel("Stock restant")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

