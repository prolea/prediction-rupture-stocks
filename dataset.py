#-----Génération des données de base-----

# Imports et configuration
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

fake = Faker("fr_FR") # Initialise Faker pour générer des noms de produits fictifs
random.seed(42) #fige l'aléatoire pour que les résultats soient fixes

# Dates
num_days = 30 
start_date = datetime.today() - timedelta(days=num_days) # Date de début des ventes
date_range = [start_date + timedelta(days=i) for i in range(num_days)] # Génère une liste de dates couvrant les 30 jours 

#Génération des clients
customers = [] #liste vide pour y ajouter les clients
for i in range(1, 1001): 
    name = fake.name()
    email = fake.email()
    location = fake.city()
    registration_date = random.choice(date_range)

    customers.append({
        "customer_id": i,
        "customer_name": name,
        "email": email,
        "location": location,
        "registration_date": registration_date.date()
    })

customers_df = pd.DataFrame(customers)
customers_df.to_csv("customers.csv", index=False, encoding="utf-8")


# Génération  des produits
categories = ["Électronique", "Vêtements", "Alimentation", "Beauté", "Sport"]
# Ajout du type de produit
product_types = ["normal"] * 25 + ["bestseller"] * 15 + ["niche"] * 10 #permet d'obtenir exactement 50% de produits normaux, 30% de bestseller et 20% de niche (50 produits au total).
random.shuffle(product_types) # Mélange la distribution des types
products = [] #liste vide pour y ajouter les produits 
for i in range(1, 51): #50 produits
    category = random.choice(categories)#Génération d'un prix réaliste en fonction de la catégorie
    if category == "Alimentation":
        price = round(random.uniform(1, 20), 2)
    elif category == "Beauté":
        price = round(random.uniform(5, 50),2)
    elif category == "Vêtements":
        price = round(random.uniform(10, 150),2)
    elif category == "Électronique":
        price = round(random.uniform(50, 1000),2)
    elif category == "Sport":
        price = round(random.uniform(10, 500),2)
    else:
        price = round(random.uniform(10, 200),2)
    product_type = product_types[i - 1]
    products.append({
        "product_id": i,
        "product_name": fake.word().capitalize(),
        "category": category,
        "price": price,
        "product_type": product_type
    })

products_df = pd.DataFrame(products) #Création du df des produits

# Attribution du stock initial en fonction du type de produit
def assign_stock(product_type):
    if product_type == "bestseller":
        return random.randint(100,200)
    elif product_type == "niche":
        return random.randint(20,80)
    else: #normal
        return random.randint(50,150)

# Création de la colonne "initial_stock" et application de la fonction à chaque ligne
products_df["initial_stock"] = products_df["product_type"].apply(assign_stock)
#Sauvegarde des produits dans un fichier csv
products_df.to_csv("products.csv", index=False, encoding="utf-8-sig")

#-----Définition des facteurs d'impact sur les ventes-----

#Création d'un coeff saisonnier pour refléter l'impact des saisons sur les ventes
seasonal_multipliers = {
    ("Vêtements", "Hiver"):1.3,
    ("Vêtements", "Été"): 0.8,
    ("Électronique", "Hiver"): 1.2,
    ("Sport", "Printemps"):1.3,
    ("Sport", "Été"): 1.4,
    ("Beauté", "Été"): 1.2,
    ("Alimentation", "Hiver"):1.1,
}

weekday_multipliers = {
    "Monday": 0.9,
    "Tuesday": 1.0,
    "Wednesday": 1.0,
    "Thursday": 1.0,
    "Friday": 1.2,
    "Saturday": 1.5,
    "Sunday": 1.3
}

promo_multipliers = 1.3

category_base_multipliers = {
    "Électronique": 1.2,
    "Vêtements": 1.0,
    "Beauté": 0.9,
    "Sport": 1.1,
    "Alimentation": 1.3
}

discount_rates = {
    "Vêtements": 0.1,
    "Électronique": 0.05,
    "Beauté": 0.15,
    "Alimentation": 0.07,
    "Sport": 0.12
}

#Définition de campagnes marketing fictives
marketing_campaigns = [
    {"name": "Buzz Tiktok", "duration": 5},
    {"name": "Influenceur A", "duration": 5},
    {"name": "TV Pub", "duration": 10}
]

#Sélection aléatoire de 5 produits concernés par chaque campagne
for i, campaign in enumerate(marketing_campaigns):
    campaign["start"] = start_date + timedelta(days=i * 7)
    campaign["end"] = campaign["start"] + timedelta(days=campaign["duration"] - 1)
    campaign["product_ids"] = random.sample(list(products_df["product_id"]), 5)

#Ajout d'événements ponctuels avec variation des taux 
special_events = [
    {
        "name":"Black Friday",
        "start_date": datetime(2025, 11, 24),
        "end_date": datetime(2025,11,24),
        "categories": None, #Toutes les catégories
        "multiplier": 1.7
    },
    {
        "name":"Soldes d'hiver",
        "start_date": datetime(2026, 1, 8),
        "end_date": datetime(2026, 2, 7),
        "categories": ["Électronique", "Vêtements", "Sport", "Beauté"], 
        "multiplier": 1.5
    },
    {
        "name":"Noël",
        "start_date": datetime(2025, 12, 20),
        "end_date": datetime(2025, 12, 24),
        "categories": ["Électronique", "Beauté"], 
        "multiplier": 1.6
    },
    {
        "name":"Soldes d'été",
        "start_date": datetime(2025, 7, 8),
        "end_date": datetime(2025, 8, 7),
        "categories": ["Électronique", "Vêtements", "Sport", "Beauté"], 
        "multiplier": 1.5
    }
]

#-----Génération des ventes-----

# Attribution des ventes pour chaque jour
sales_data = []
customer_ids = customers_df["customer_id"].tolist() #Création de la liste des IDs clients 

for day in date_range:
    for _, product in products_df.iterrows(): # _, sert à ignorer l'index de la ligne; iterrows() permet d’accéder aux valeurs de chaque produit, afin de récupérer son product_id, product_type, etc.
        # Définition des ventes de base selon le type de produit
        units_sold = random.randint(5, 15) if product["product_type"] == "bestseller" else random.randint(0, 5) if product["product_type"] == "niche" else random.randint(1, 10)
        #Ajout d'un éventuel effet promotion
        is_promo = random.choice([0,1]) if random.random() < 0.2 else 0 # 20% de chance d'avoir une promo
        if is_promo: units_sold += random.randint(3,10)

        season = "Hiver" if day.month in [12, 1, 2] else "Printemps" if day.month in [3, 4, 5] else "Été" if day.month in [6, 7, 8] else "Automne"
        units_sold = int(units_sold * seasonal_multipliers.get((product["category"], season), 1.0))
        weekday = day.strftime("%A") # Nom du jour (ex: Lundi)
        units_sold = int(units_sold * weekday_multipliers.get(weekday, 1.0))
        units_sold = int(units_sold * category_base_multipliers.get(product["category"], 1.0))
        if is_promo: units_sold = int(units_sold * promo_multipliers)

        #Calcul du prix final avec remise
        base_price = product["price"]
        if is_promo:
            discount_rate = discount_rates.get(product["category"], 0) #récupère la remise selon la catégorie
            final_price = round(base_price * (1 - discount_rate), 2)
            discount_applied = 1
        else:
            final_price = base_price
            discount_applied = 0 

        #Ajout d'un bruit gaussien pour simuler des imprévus réels
        units_sold = max(0, int(units_sold + np.random.normal(0, 2))) #arrondi et minimum 0

        #initialisation
        campaign_name = None
        #Application de l'effet de campagne marketing
        for campaign in marketing_campaigns:
            if campaign["start"] <= day <= campaign["end"] and product["product_id"] in campaign["product_ids"]:
                units_sold = int(units_sold * 1.5) #Boost de 50%
                campaign_name = campaign["name"]
                break #Un seul boost par jour suffit
        
        #Initialisation
        event_name = None
        #Application de l'effet événement spécial
        for event in special_events:
            if event["start_date"].date() <= day.date() <= event["end_date"].date():
                if event["categories"] is None or product["category"] in event["categories"]:
                    units_sold = int(units_sold * event["multiplier"])
                    event_name = event["name"]
                    break

        #Choix aléatoire d'un client existant 
        customer_id = random.choice(customer_ids)
        # Enregistrement des données de vente
        sales_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "product_id": product["product_id"],
            "customer_id": customer_id,
            "units_sold": units_sold,
            "is_promotion": is_promo,
            "weekday": weekday,
            "season": season,
            "campaign_name": campaign_name,
            "event": event_name,
            "price": base_price,
            "discount_applied": discount_applied,
            "final_price": final_price
        })

sales_df = pd.DataFrame(sales_data)
sales_df["date"] = pd.to_datetime(sales_df["date"]) # Convertit en format datetime

#-----Partie Fusion et enrichissement-----

#Choix des colonnes à fusionner
columns_to_merge = ["product_id", "product_type", "category", "initial_stock", "product_name", "price"]
#Fusion des colonnes choisies
sales_df = sales_df.merge(products_df[columns_to_merge], on="product_id", how="left")

#Renommer price_x en original_price, suppression de la colonne price en trop
sales_df = sales_df.rename(columns={"price_x": "original_price"})
sales_df.drop(columns=["price_y"], inplace=True)

#Définition des modes de paiement et leurs probabilités
payment_methods = [
    ("Carte bancaire", 0.5),
    ("Paypal", 0.25),
    ("Apple Pay", 0.15),
    ("Carte cadeau", 0.1)
]
#Ajout de la colonne payment_method dans sales_df
sales_df["payment_method"] = np.random.choice(
    [m[0] for m in payment_methods],
    size=len(sales_df),
    p=[m[1] for m in payment_methods]
)

#Comptage du nombre de commandes par client
order_counts = sales_df["customer_id"].value_counts()
#Reclassement de chaque client selon son nombre d'achats
def get_customer_type(order_count): return "VIP" if order_count >= 5 else "returning" if order_count >= 2 else "new" 
customers_df["customer_type"] = customers_df["customer_id"].map(order_counts).fillna(0).astype(int).apply(get_customer_type)

# Calcul du stock restant en soustrayant les ventes cumulées du stock initial
sales_df["cumulative_sales"] = sales_df.groupby("product_id")["units_sold"].cumsum() # Permet de suivre la progression des ventes cumulées pour chaque product_id
sales_df["remaining_stock"] = sales_df["initial_stock"] - sales_df["cumulative_sales"]


#Calcul du chiffre d'affaires par produit
sales_df["revenue"] = sales_df["units_sold"] * sales_df["final_price"]
revenue_per_product = (
    sales_df.groupby("product_id")["revenue"]
    .sum()
    .reset_index()
    .merge(products_df[["product_id", "product_name", "category", "product_type"]], on="product_id", how="left")
)

top_products = revenue_per_product.sort_values(by="revenue", ascending=False).head(10)

# Ajout du mode de livraison aléatoire
delivery_modes = ["standard", "express", "pickup"]
sales_df["delivery_mode"] = np.random.choice(delivery_modes, size=len(sales_df))
 
#Probabilité de retour ou annulation (par défaut 5%)
return_prob = 0.05
#Création de la colonne is_returned
sales_df["is_returned"] = np.random.choice([0, 1], size=len(sales_df), p=[1 - return_prob, return_prob])

#Dictionnaire des motifs de retour par catégorie avec leurs probabilités
category_return_reasons = {
    "Vêtements": [("taille", 0.6), ("changement d'avis", 0.3), ("défaut", 0.1)],
    "Électronique": [("défaut", 0.5), ("produit non conforme", 0.4), ("changement d'avis", 0.1)],
    "Beauté": [("changement d'avis", 0.8), ("produit non conforme", 0.2)],
    "Alimentation": [("produit non conforme", 0.7), ("livraison tardive", 0.3)],
    "Sport" : [("taille", 0.5), ("défaut", 0.3), ("changement d'avis", 0.2)]
}

#Fonction de génération du motif de retour
def generate_reason(row):
    if row["is_returned"]:
        reasons = category_return_reasons.get(row["category"], [("changement d'avis", 1.0)])
        motifs, weights = zip(*reasons)
        return np.random.choice(motifs, p=weights)
    return None

#Application de la fonction
sales_df["return_reason"] = sales_df.apply(generate_reason, axis=1)

#Fonction de génération de note
def generate_rating(row):
    if row["is_returned"]:
        return None

    #Note de base selon le type de produit
    base_rating = {
        "bestseller": 4.5,
        "normal": 4.0,
        "niche": 4.5
    }.get(row["product_type"], 4.0)

    #Bonus si promo
    if row["discount_applied"] > 0:
        base_rating += 0.3
    
    #Bruit aléatoire pour varier un peu les notes
    noise = np.random.normal(0, 0.5)
    rating = base_rating + noise
    #arrondi entre 1.0 et 5.0
    return round(min(max(rating, 1), 5), 1)

#Application 
sales_df["rating"] = sales_df.apply(generate_rating, axis=1)

#-----Graphiques-----

#-----Graphique top 10 produits par chiffre d'affaires-----

palette = sns.color_palette("viridis", n_colors=len(top_products))#palette dégradée sur N couleurs
plt.figure(figsize=(10, 6))
sns.barplot(x="revenue", y="product_name", data=top_products, hue="revenue", palette="viridis", legend=False, dodge=False)
plt.title("Top 10 des produits par chiffre d'affaires")
plt.xlabel("Chiffre d'affaires (€)")
plt.ylabel("produit")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

#-----Graphique stock moyen restant par catégorie-----
sales_df["remaining_stock"] = sales_df["remaining_stock"].clip(lower=0) # Évite les stocks négatifs en remplaçant les valeurs négatives pas 0

#Distribution des stocks par catégorie
remaining_stock_by_category = (sales_df.groupby("category")["remaining_stock"].mean().reset_index())

#Graphique distribution des stocks par catégorie
palette = sns.color_palette("coolwarm", n_colors=len(remaining_stock_by_category))
plt.figure(figsize=(8,5))
sns.barplot(x="category", y="remaining_stock", data=remaining_stock_by_category,hue="remaining_stock", palette=palette)
plt.title("Stock moyen restant par catégorie de produit")
plt.xlabel("Catégorie")
plt.ylabel("Stock restant moyen")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--")
plt.tight_layout()
plt.show()

#-----Graphique Nombre de commandes par ville-----

sales_df["date"] = pd.to_datetime(sales_df["date"])
sales_df["order_group"] = sales_df["customer_id"].astype(str) + "-" + sales_df["date"].dt.strftime("%Y-%m-%d")
sales_df["order_id"] = sales_df["order_group"].astype("category").cat.codes + 1
sales_df.drop("order_group", axis=1, inplace=True)

orders_by_city = (
    sales_df[["customer_id", "order_id"]].drop_duplicates()
    .merge(customers_df[["customer_id", "location"]], on="customer_id", how="left")
    .groupby("location")["order_id"].nunique()
    .reset_index()
    .sort_values(by="order_id", ascending=False)
    .head(10)
    .rename(columns={"order_id": "num_orders"})
)

#Graphique top 10 des villes par nombre de commandes
palette = sns.color_palette("magma", n_colors=len(orders_by_city))
plt.figure(figsize=(10,6))
sns.barplot(x="num_orders", y="location", data=orders_by_city, hue="num_orders", palette=palette)
plt.title("Top 10 des villes par nombre de commandes")
plt.xlabel("Nombre de commandes")
plt.ylabel("Ville")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

# Réorganisation des colonnes
ordered_columns = [
    "date","order_id", "customer_id", "payment_method", 
    "product_id", "product_name", "category", "product_type", 
    "units_sold", "is_promotion", "original_price", "discount_applied", "final_price",
    "initial_stock", "remaining_stock", "cumulative_sales", "revenue",
    "delivery_mode", "is_returned", "return_reason",
    "rating",
    "weekday", "season", "campaign_name", "event" 
]
sales_df = sales_df[ordered_columns]
sales_df.to_csv("sales_final.csv", index=False)

print(sales_df.columns)