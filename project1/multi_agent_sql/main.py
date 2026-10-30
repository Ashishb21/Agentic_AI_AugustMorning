"""
Main entry point for the multi-agent customer service system.
Demonstrates how to run the system with sample queries.
"""

from pathlib import Path
import json

try:
    from graph import create_graph
    from state_schema import CustomerServiceState
except ImportError:
    from .graph import create_graph
    from .state_schema import CustomerServiceState

from langchain_core.messages import HumanMessage


def get_initial_state(query: str) -> CustomerServiceState:
    """
    Create initial state for a new query.

    Args:
        query: User's input query

    Returns:
        Initial CustomerServiceState
    """
    return {
        "messages": [HumanMessage(content=query)],
        "user_query": query,
        "query_type": "unclear",
        "current_agent": "none",
        "sql_query": "",
        "sql_result": {},
        "agent_response": "",
        "needs_clarification": False,
        "is_complete": False,
        "escalate_to_human": False,
        "customer_id": None,
        "order_id": None,
        "confidence_score": 0.0,
    }


def run_customer_service(query: str, debug: bool = False) -> str:
    """
    Run the multi-agent system for a customer query.

    Args:
        query: Customer's input query
        debug: Whether to print debug information

    Returns:
        Final agent response
    """

    print(f"\n{'='*70}")
    print(f"CUSTOMER QUERY: {query}")
    print(f"{'='*70}")

    # Create graph
    app = create_graph()

    # Get initial state
    initial_state = get_initial_state(query)

    # Run the graph
    try:
        final_state = app.invoke(initial_state)

        # Extract response
        response = final_state.get("agent_response", "No response generated")

        print(f"\n{'='*70}")
        print(f"FINAL RESPONSE")
        print(f"{'='*70}")
        print(response)

        if debug:
            print(f"\n{'='*70}")
            print("DEBUG INFO")
            print(f"{'='*70}")
            print(f"Query Type: {final_state.get('query_type')}")
            print(f"Confidence: {final_state.get('confidence_score'):.2f}")
            print(f"Final Agent: {final_state.get('current_agent')}")
            print(f"Complete: {final_state.get('is_complete')}")

        return response

    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"\nERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return error_msg


def run_demo():
    """Run demonstration with sample queries."""

    print("\n" + "="*70)
    print("MULTI-AGENT CUSTOMER SERVICE SYSTEM - DEMO")
    print("="*70)

    # Sample queries demonstrating different capabilities
    demo_queries = [
        "What's the status of order #1001?",
        "Do you have any laptops in stock?",
        "I want a refund for order #1002",
        "Show me your top selling products",
        "Can you help me with my order? My email is john.doe@email.com",
    ]

    for query in demo_queries:
        run_customer_service(query, debug=True)
        print("\n")


def interactive_mode():
    """
    Run in interactive mode, accepting user input.
    """

    print("\n" + "="*70)
    print("MULTI-AGENT CUSTOMER SERVICE SYSTEM - INTERACTIVE MODE")
    print("="*70)
    print("Enter 'quit' to exit, 'db' to check database status\n")

    # Check if database exists
    db_path = Path(__file__).parent / "customer_service.db"
    if not db_path.exists():
        print("ERROR: Database not found!")
        print("Please run: python database_setup.py")
        return

    while True:
        try:
            query = input("\nYour query: ").strip()

            if query.lower() == "quit":
                print("Thank you for using our service!")
                break

            if query.lower() == "db":
                print(f"Database exists at: {db_path}")
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM customers")
                customers = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM orders")
                orders = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM products")
                products = cursor.fetchone()[0]

                print(f"Customers: {customers}, Orders: {orders}, Products: {products}")
                conn.close()
                continue

            if not query:
                continue

            run_customer_service(query, debug=False)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            run_demo()
        elif sys.argv[1] == "interactive":
            interactive_mode()
        else:
            # Single query
            query = " ".join(sys.argv[1:])
            run_customer_service(query, debug=True)
    else:
        # Default: interactive mode
        interactive_mode()
