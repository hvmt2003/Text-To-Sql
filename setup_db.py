import sqlite3
import pandas as pd
import random
import os

DB_NAME = "local_sales.db"

def create_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Create Tables
    print(f"Creating tables in {DB_NAME}...")
    
    # Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        ProductID INTEGER PRIMARY KEY,
        ProductName TEXT NOT NULL,
        Category TEXT NOT NULL,
        Price REAL NOT NULL,
        StockQuantity INTEGER NOT NULL
    )
    ''')

    # Customers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customers (
        CustomerID INTEGER PRIMARY KEY,
        FullName TEXT NOT NULL,
        Email TEXT NOT NULL,
        Country TEXT NOT NULL,
        JoinDate DATE NOT NULL
    )
    ''')

    # Orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        OrderID INTEGER PRIMARY KEY,
        CustomerID INTEGER,
        ProductID INTEGER,
        OrderDate DATE NOT NULL,
        Quantity INTEGER NOT NULL,
        TotalAmount REAL NOT NULL,
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
    )
    ''')

    # 2. Insert Dummy Data
    print("Inserting data...")

    products = [
        (1, "Laptop Pro X", "Electronics", 1200.00, 50),
        (2, "Smartphone Z", "Electronics", 800.00, 100),
        (3, "Noise Cancelling Headphones", "Audio", 250.00, 200),
        (4, "Ergonomic Chair", "Furniture", 300.00, 30),
        (5, "Running Shoes", "Apparel", 120.00, 75),
        (6, "Coffee Maker", "Appliances", 80.00, 60),
        (7, "4K Monitor", "Electronics", 400.00, 40),
        (8, "Mechanical Keyboard", "Electronics", 150.00, 80),
    ]
    cursor.executemany("INSERT INTO Products VALUES (?,?,?,?,?)", products)

    customers = [
        (101, "Alice Smith", "alice@example.com", "USA", "2023-01-15"),
        (102, "Bob Jones", "bob@test.com", "UK", "2023-02-20"),
        (103, "Charlie Brown", "charlie@domain.com", "Canada", "2023-03-10"),
        (104, "Diana Prince", "diana@themyscira.com", "Greece", "2023-04-05"),
        (105, "Evan Wright", "evan@writes.com", "Australia", "2023-05-12"),
    ]
    cursor.executemany("INSERT INTO Customers VALUES (?,?,?,?,?)", customers)

    # Generate some orders
    orders = []
    order_id = 1001
    for _ in range(20):
        customer = random.choice(customers)
        product = random.choice(products)
        qty = random.randint(1, 3)
        total = product[3] * qty
        date = f"2023-0{random.randint(1,9)}-{random.randint(10,28)}"
        
        orders.append((order_id, customer[0], product[0], date, qty, total))
        order_id += 1
        
    cursor.executemany("INSERT INTO Orders VALUES (?,?,?,?,?,?)", orders)

    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    create_database()
