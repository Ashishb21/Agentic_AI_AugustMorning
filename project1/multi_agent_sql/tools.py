"""
SQL tools for the multi-agent customer service system.
Provides safe, parameterized database query functions.
"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List

# Database path
DB_PATH = Path(__file__).parent / "customer_service.db"


def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def dict_from_row(row) -> dict:
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    return dict(row)


# ==================== QUERY AGENT TOOLS ====================

def search_order_by_id(order_id: int) -> Dict[str, Any]:
    """
    Search for an order by order ID.

    Args:
        order_id: The order ID to search for

    Returns:
        Dictionary with order details or error message
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT o.*, c.name as customer_name, c.email, p.name as product_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            WHERE o.order_id = ?
        """, (order_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {"found": True, "order": dict(row)}
        else:
            return {"found": False, "error": f"Order {order_id} not found"}

    except Exception as e:
        return {"found": False, "error": str(e)}


def search_order_by_customer_email(email: str) -> Dict[str, Any]:
    """
    Search for orders by customer email.

    Args:
        email: Customer email address

    Returns:
        Dictionary with list of orders or error message
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT o.*, c.name as customer_name, p.name as product_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            WHERE c.email = ?
            ORDER BY o.order_date DESC
        """, (email,))

        rows = cursor.fetchall()
        conn.close()

        if rows:
            return {
                "found": True,
                "customer_email": email,
                "order_count": len(rows),
                "orders": [dict(row) for row in rows]
            }
        else:
            return {"found": False, "error": f"No orders found for {email}"}

    except Exception as e:
        return {"found": False, "error": str(e)}


# ==================== SALES AGENT TOOLS ====================

def search_products(search_query: str, category: str = None) -> Dict[str, Any]:
    """
    Search for products by name or category.

    Args:
        search_query: Product name or keyword to search
        category: Optional product category to filter by

    Returns:
        Dictionary with list of matching products
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if category:
            cursor.execute("""
                SELECT * FROM products
                WHERE (name LIKE ? OR description LIKE ?)
                AND category = ?
                ORDER BY name
            """, (f"%{search_query}%", f"%{search_query}%", category))
        else:
            cursor.execute("""
                SELECT * FROM products
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name
            """, (f"%{search_query}%", f"%{search_query}%"))

        rows = cursor.fetchall()
        conn.close()

        if rows:
            return {
                "found": True,
                "product_count": len(rows),
                "products": [dict(row) for row in rows]
            }
        else:
            return {"found": False, "error": f"No products found for '{search_query}'"}

    except Exception as e:
        return {"found": False, "error": str(e)}


def get_product_details(product_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.

    Args:
        product_id: The product ID

    Returns:
        Dictionary with product details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"found": True, "product": dict(row)}
        else:
            return {"found": False, "error": f"Product {product_id} not found"}

    except Exception as e:
        return {"found": False, "error": str(e)}


def check_stock_availability(product_id: int, quantity: int = 1) -> Dict[str, Any]:
    """
    Check if a product has sufficient stock.

    Args:
        product_id: The product ID
        quantity: Quantity needed

    Returns:
        Dictionary with availability information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT product_id, name, stock_quantity FROM products WHERE product_id = ?",
            (product_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            product = dict(row)
            available = product["stock_quantity"] >= quantity
            return {
                "available": available,
                "product_name": product["name"],
                "requested_quantity": quantity,
                "stock_quantity": product["stock_quantity"],
                "shortage": max(0, quantity - product["stock_quantity"])
            }
        else:
            return {"available": False, "error": f"Product {product_id} not found"}

    except Exception as e:
        return {"available": False, "error": str(e)}


# ==================== REFUND AGENT TOOLS ====================

def check_refund_eligibility(order_id: int) -> Dict[str, Any]:
    """
    Check if an order is eligible for refund.

    Args:
        order_id: The order ID

    Returns:
        Dictionary with eligibility information and reasons
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {"eligible": False, "error": f"Order {order_id} not found"}

        order = dict(row)

        # Check if already refunded
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM refunds WHERE order_id = ? AND status = 'approved'",
                       (order_id,))
        refund_count = cursor.fetchone()[0]
        conn.close()

        if refund_count > 0:
            return {
                "eligible": False,
                "order_id": order_id,
                "reason": "Order already has an approved refund"
            }

        # Check order status (cancelled orders can't be refunded)
        if order["status"] == "cancelled":
            return {
                "eligible": False,
                "order_id": order_id,
                "reason": "Cannot refund cancelled orders"
            }

        # Order is eligible
        return {
            "eligible": True,
            "order_id": order_id,
            "status": order["status"],
            "total_price": order["total_price"],
            "order_date": order["order_date"]
        }

    except Exception as e:
        return {"eligible": False, "error": str(e)}


def create_refund_request(order_id: int, reason: str, amount: float = None) -> Dict[str, Any]:
    """
    Create a refund request for an order.

    Args:
        order_id: The order ID
        reason: Reason for the refund
        amount: Refund amount (if None, uses order total)

    Returns:
        Dictionary with refund request details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get order total if amount not specified
        if amount is None:
            cursor.execute("SELECT total_price FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            if row:
                amount = row[0]
            else:
                return {"success": False, "error": f"Order {order_id} not found"}

        # Create refund request
        cursor.execute("""
            INSERT INTO refunds (order_id, reason, refund_amount, status)
            VALUES (?, ?, ?, 'pending')
        """, (order_id, reason, amount))

        refund_id = cursor.lastrowid

        # Update order status
        cursor.execute(
            "UPDATE orders SET status = 'refund_requested' WHERE order_id = ?",
            (order_id,)
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "refund_id": refund_id,
            "order_id": order_id,
            "refund_amount": amount,
            "status": "pending",
            "message": f"Refund request created. Amount: ${amount:.2f}"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== ANALYTICS AGENT TOOLS ====================

def get_sales_report() -> Dict[str, Any]:
    """
    Generate a sales report with key metrics.

    Returns:
        Dictionary with sales statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total revenue
        cursor.execute(
            "SELECT SUM(total_price) FROM orders WHERE status IN ('delivered', 'shipped')"
        )
        total_revenue = cursor.fetchone()[0] or 0

        # Order count by status
        cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
        order_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # Average order value
        cursor.execute("SELECT AVG(total_price) FROM orders WHERE status IN ('delivered', 'shipped')")
        avg_order_value = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_revenue": total_revenue,
            "average_order_value": avg_order_value,
            "total_orders": sum(order_stats.values()),
            "order_stats": order_stats
        }

    except Exception as e:
        return {"error": str(e)}


def get_top_products(limit: int = 5) -> Dict[str, Any]:
    """
    Get the top selling products.

    Args:
        limit: Number of top products to return

    Returns:
        Dictionary with top products and sales info
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.product_id, p.name, p.category, COUNT(o.order_id) as order_count,
                   SUM(o.quantity) as total_quantity, SUM(o.total_price) as total_revenue
            FROM products p
            LEFT JOIN orders o ON p.product_id = o.product_id AND o.status IN ('delivered', 'shipped')
            GROUP BY p.product_id
            ORDER BY total_revenue DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        products = []
        for row in rows:
            products.append({
                "product_id": row[0],
                "name": row[1],
                "category": row[2],
                "order_count": row[3] or 0,
                "total_quantity": row[4] or 0,
                "total_revenue": row[5] or 0
            })

        return {"top_products": products}

    except Exception as e:
        return {"error": str(e)}


def get_customer_stats() -> Dict[str, Any]:
    """
    Get customer statistics.

    Returns:
        Dictionary with customer information and insights
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total customers
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]

        # Customers by number of orders
        cursor.execute("""
            SELECT c.customer_id, c.name, COUNT(o.order_id) as order_count,
                   SUM(o.total_price) as total_spent
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id
            ORDER BY total_spent DESC
        """)

        customer_data = []
        for row in cursor.fetchall():
            customer_data.append({
                "customer_id": row[0],
                "name": row[1],
                "order_count": row[2] or 0,
                "total_spent": row[3] or 0
            })

        conn.close()

        return {
            "total_customers": total_customers,
            "customer_stats": customer_data
        }

    except Exception as e:
        return {"error": str(e)}
