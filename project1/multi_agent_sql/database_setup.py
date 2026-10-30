"""
Database setup for the multi-agent customer service system.
Creates a SQLite database with sample data for customers, products, orders, and refunds.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "customer_service.db"


def create_database():
    """Create SQLite database with schema and sample data."""

    # Remove existing database if it exists
    if DB_PATH.exists():
        os.remove(DB_PATH)

    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    print("Creating database schema...")

    # Create customers table
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create products table
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        category TEXT
    )
    """)

    # Create orders table
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER,
        total_price REAL,
        status TEXT DEFAULT 'pending',
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Create refunds table
    cursor.execute("""
    CREATE TABLE refunds (
        refund_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        reason TEXT,
        status TEXT DEFAULT 'pending',
        refund_amount REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    """)

    print("Inserting sample customers...")

    # Insert sample customers
    customers = [
        ("John Doe", "john.doe@email.com", "555-0101"),
        ("Jane Smith", "jane.smith@email.com", "555-0102"),
        ("Bob Johnson", "bob.johnson@email.com", "555-0103"),
        ("Alice Williams", "alice.williams@email.com", "555-0104"),
        ("Charlie Brown", "charlie.brown@email.com", "555-0105"),
    ]

    cursor.executemany(
        "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
        customers
    )

    print("Inserting sample products...")

    # Insert sample products
    products = [
        ("Laptop Pro", "High-performance laptop with 16GB RAM and 512GB SSD", 1299.99, 15, "Electronics"),
        ("Smartphone X", "Latest smartphone with advanced camera system", 899.99, 25, "Electronics"),
        ("Wireless Headphones", "Noise-cancelling wireless headphones with 30h battery", 199.99, 40, "Audio"),
        ("USB-C Cable", "High-speed USB-C charging and data cable", 19.99, 100, "Accessories"),
        ("Laptop Stand", "Adjustable aluminum laptop stand for desk setup", 49.99, 30, "Accessories"),
        ("Monitor 27inch", "4K ultra-wide monitor for professional work", 499.99, 10, "Electronics"),
        ("Mechanical Keyboard", "RGB mechanical keyboard with custom switches", 149.99, 20, "Peripherals"),
        ("Portable SSD", "1TB portable solid-state drive with USB 3.1", 129.99, 35, "Storage"),
        ("Webcam HD", "1080p HD webcam with built-in microphone", 79.99, 25, "Peripherals"),
        ("Phone Case", "Durable protective phone case with air cushion technology", 24.99, 50, "Accessories"),
    ]

    cursor.executemany(
        """INSERT INTO products (name, description, price, stock_quantity, category)
           VALUES (?, ?, ?, ?, ?)""",
        products
    )

    print("Inserting sample orders...")

    # Insert sample orders with various statuses and dates
    now = datetime.now()
    orders = [
        (1, 1, 1, 1299.99, "delivered", now - timedelta(days=30)),
        (1, 2, 1, 899.99, "shipped", now - timedelta(days=5)),
        (2, 3, 1, 199.99, "delivered", now - timedelta(days=60)),
        (2, 4, 2, 39.98, "pending", now - timedelta(hours=2)),
        (3, 5, 1, 49.99, "delivered", now - timedelta(days=15)),
        (3, 6, 1, 499.99, "shipped", now - timedelta(days=3)),
        (4, 7, 1, 149.99, "pending", now - timedelta(hours=12)),
        (4, 8, 1, 129.99, "delivered", now - timedelta(days=45)),
        (5, 9, 1, 79.99, "shipped", now - timedelta(days=8)),
        (5, 10, 1, 24.99, "delivered", now - timedelta(days=20)),
        (1, 3, 2, 399.98, "pending", now - timedelta(hours=1)),
        (2, 1, 1, 1299.99, "cancelled", now - timedelta(days=25)),
        (3, 4, 3, 59.97, "delivered", now - timedelta(days=35)),
        (4, 2, 1, 899.99, "pending", now - timedelta(hours=6)),
        (5, 6, 1, 499.99, "delivered", now - timedelta(days=12)),
    ]

    cursor.executemany(
        """INSERT INTO orders (customer_id, product_id, quantity, total_price, status, order_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        orders
    )

    print("Inserting sample refunds...")

    # Insert sample refunds
    refunds = [
        (12, "Product doesn't work as expected", "approved", 1299.99, now - timedelta(days=20)),
        (4, "Changed my mind", "pending", 39.98, now - timedelta(hours=1)),
        (7, "Wrong product received", "rejected", 149.99, now - timedelta(days=5)),
    ]

    cursor.executemany(
        """INSERT INTO refunds (order_id, reason, status, refund_amount, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        refunds
    )

    # Commit changes
    conn.commit()

    print(f"\nDatabase created successfully at: {DB_PATH}")
    print_database_summary(cursor)

    conn.close()


def print_database_summary(cursor):
    """Print summary of database contents."""
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)

    # Customer count
    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"Total Customers: {cursor.fetchone()[0]}")

    # Product count
    cursor.execute("SELECT COUNT(*) FROM products")
    print(f"Total Products: {cursor.fetchone()[0]}")

    # Order count by status
    cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
    print("\nOrders by Status:")
    for status, count in cursor.fetchall():
        print(f"  - {status}: {count}")

    # Refund count by status
    cursor.execute("SELECT status, COUNT(*) FROM refunds GROUP BY status")
    print("\nRefunds by Status:")
    for status, count in cursor.fetchall():
        print(f"  - {status}: {count}")

    # Total revenue
    cursor.execute("SELECT SUM(total_price) FROM orders WHERE status IN ('delivered', 'shipped')")
    revenue = cursor.fetchone()[0] or 0
    print(f"\nTotal Revenue (delivered/shipped): ${revenue:.2f}")

    print("="*60)


if __name__ == "__main__":
    create_database()
