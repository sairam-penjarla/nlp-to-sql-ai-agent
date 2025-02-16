import sqlite3
import json
import pandas as pd

# Database file name
DB_FILE = "inventory.db"

# Function to create inventory table
def create_inventory_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_id INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            supplier TEXT,
            purchase_date TEXT,
            expiry_date TEXT,
            warehouse_location TEXT,
            stock_status TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Inventory table created successfully.")

# Function to insert data from JSON file into the inventory table
def insert_inventory_data(json_file):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(json_file, "r") as file:
        data = json.load(file)

    for item in data:
        cursor.execute('''
            INSERT INTO inventory (item_id, item_name, category, quantity, price_per_unit, 
                                   supplier, purchase_date, expiry_date, warehouse_location, stock_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item["item_id"],
            item["item_name"],
            item["category"],
            item["quantity"],
            item["price_per_unit"],
            item["supplier"],
            item["purchase_date"],
            item["expiry_date"],
            item["warehouse_location"],
            item["stock_status"]
        ))

    conn.commit()
    conn.close()
    print("Inventory data inserted successfully.")

if __name__ == "__main__":
    create_inventory_table()  # Create table
    insert_inventory_data("inventory.json")  # Insert data from JSON