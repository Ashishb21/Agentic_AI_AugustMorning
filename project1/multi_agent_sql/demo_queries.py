"""
Demo queries for testing the multi-agent customer service system.
Run with: python -m pytest demo_queries.py -v -s
"""

from main import run_customer_service, get_initial_state
from graph import create_graph
import pytest


class TestQueryAgent:
    """Tests for order tracking queries"""

    def test_order_status_by_id(self):
        """Test searching for order by ID"""
        app = create_graph()
        state = get_initial_state("What's the status of order #1001?")
        result = app.invoke(state)
        assert result["is_complete"] == True
        assert "1001" in result["agent_response"]

    def test_order_status_by_email(self):
        """Test searching for orders by email"""
        app = create_graph()
        state = get_initial_state("Can you check my orders? My email is john.doe@email.com")
        result = app.invoke(state)
        assert result["is_complete"] == True


class TestSalesAgent:
    """Tests for product information queries"""

    def test_laptop_search(self):
        """Test searching for laptops"""
        app = create_graph()
        state = get_initial_state("Do you have any laptops available?")
        result = app.invoke(state)
        assert result["is_complete"] == True
        assert "Laptop" in result["agent_response"]

    def test_product_recommendation(self):
        """Test product recommendations"""
        app = create_graph()
        state = get_initial_state("What headphones do you recommend?")
        result = app.invoke(state)
        assert result["is_complete"] == True


class TestRefundAgent:
    """Tests for refund request handling"""

    def test_refund_request(self):
        """Test creating a refund request"""
        app = create_graph()
        state = get_initial_state("I'd like to return order #1002")
        result = app.invoke(state)
        # Refund request should be processed
        assert "refund" in result["agent_response"].lower() or "not eligible" in result["agent_response"].lower()


class TestAnalyticsAgent:
    """Tests for analytics queries"""

    def test_sales_report(self):
        """Test generating sales report"""
        app = create_graph()
        state = get_initial_state("Can you show me the sales report?")
        result = app.invoke(state)
        assert result["is_complete"] == True
        assert "$" in result["agent_response"]

    def test_top_products(self):
        """Test getting top products"""
        app = create_graph()
        state = get_initial_state("What are our top selling products?")
        result = app.invoke(state)
        assert result["is_complete"] == True


class TestClassificationAccuracy:
    """Tests for query classification"""

    def test_classify_order_status(self):
        """Test classification of order status query"""
        app = create_graph()
        state = get_initial_state("Where is my order?")
        result = app.invoke(state)
        assert result["query_type"] == "order_status"

    def test_classify_product_info(self):
        """Test classification of product info query"""
        app = create_graph()
        state = get_initial_state("Tell me about your laptops")
        result = app.invoke(state)
        assert result["query_type"] == "product_info"

    def test_classify_refund(self):
        """Test classification of refund query"""
        app = create_graph()
        state = get_initial_state("I want a refund")
        result = app.invoke(state)
        assert result["query_type"] == "refund"

    def test_classify_analytics(self):
        """Test classification of analytics query"""
        app = create_graph()
        state = get_initial_state("What are our sales numbers?")
        result = app.invoke(state)
        assert result["query_type"] == "analytics"


# ==================== INTERACTIVE DEMO FUNCTIONS ====================

def demo_order_tracking():
    """Demo: Order tracking workflow"""
    print("\n" + "="*70)
    print("DEMO: ORDER TRACKING")
    print("="*70)

    queries = [
        "What's the status of order #1001?",
        "Can you check my orders? Email: jane.smith@email.com",
        "Where is my order #1005?",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        run_customer_service(query, debug=False)


def demo_product_search():
    """Demo: Product search workflow"""
    print("\n" + "="*70)
    print("DEMO: PRODUCT SEARCH")
    print("="*70)

    queries = [
        "Do you have any laptops?",
        "What headphones do you have?",
        "Show me portable SSDs",
        "I'm looking for a webcam",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        run_customer_service(query, debug=False)


def demo_refund_processing():
    """Demo: Refund processing workflow"""
    print("\n" + "="*70)
    print("DEMO: REFUND PROCESSING")
    print("="*70)

    queries = [
        "I want a refund for order #1001",
        "Can I return order #1002? The product doesn't work.",
        "Is order #1005 eligible for refund?",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        run_customer_service(query, debug=False)


def demo_analytics():
    """Demo: Analytics reporting"""
    print("\n" + "="*70)
    print("DEMO: ANALYTICS REPORTING")
    print("="*70)

    queries = [
        "Show me our sales report",
        "What are the top selling products?",
        "Give me customer statistics",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        run_customer_service(query, debug=False)


if __name__ == "__main__":
    print("Run individual demos or use pytest for unit tests")
    print("\nUsage:")
    print("  pytest demo_queries.py -v -s          # Run unit tests")
    print("  python demo_queries.py order           # Demo order tracking")
    print("  python demo_queries.py product         # Demo product search")
    print("  python demo_queries.py refund          # Demo refund processing")
    print("  python demo_queries.py analytics       # Demo analytics")

    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "order":
            demo_order_tracking()
        elif sys.argv[1] == "product":
            demo_product_search()
        elif sys.argv[1] == "refund":
            demo_refund_processing()
        elif sys.argv[1] == "analytics":
            demo_analytics()
