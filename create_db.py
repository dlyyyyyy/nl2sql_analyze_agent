import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('sales.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    date TEXT,
    region TEXT,
    product TEXT,
    sales_amount REAL,
    collection_amount REAL,
    overdue_days INTEGER
)
''')

regions = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']
products = ['A_product', 'B_product', 'C_product']
start_date = datetime(2025, 1, 1)
data = []

for i in range(200):
    date = start_date + timedelta(days=random.randint(0, 90))
    region = random.choice(regions)
    product = random.choice(products)
    sales_amount = round(random.uniform(10000, 100000), 2)
    collection_rate = random.uniform(0.6, 1.0)
    collection_amount = round(sales_amount * collection_rate, 2)
    overdue_days = random.randint(0, 60) if collection_amount < sales_amount else 0
    data.append([i+1, date.strftime('%Y-%m-%d'), region, product, sales_amount, collection_amount, overdue_days])

df = pd.DataFrame(data, columns=['id', 'date', 'region', 'product', 'sales_amount', 'collection_amount', 'overdue_days'])
df.to_sql('orders', conn, if_exists='replace', index=False)
conn.close()

print("Data created successfully! File: sales.db")