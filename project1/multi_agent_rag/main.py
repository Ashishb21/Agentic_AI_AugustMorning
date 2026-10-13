"""
Main entry point for the agentic RAG system.
Demonstrates how to run the system with sample queries.
"""

from pathlib import Path

try:
    from graph import create_graph
    from state_schema import RAGState
except ImportError:
    from .graph import create_graph
    from .state_schema import RAGState

from langchain_core.messages import HumanMessage


def get_initial_state(query: str) -> RAGState:
    """
    Create initial state for a new query.

    Args:
        query: User's input query

    Returns:
        Initial RAGState with all fields properly initialized
    """
    return {
        "messages": [HumanMessage(content=query)],
        "user_query": query,
        "query_type": "unclear",
        "current_agent": "none",
        "retrieved_documents": [],
        "document_scores": [],
        "retrieval_method": "",
        "generated_answer": "",
        "citations": [],
        "confidence_score": 0.0,
        "is_complete": False,
        "needs_clarification": False,
        "agent_response": "",
        "tool_calls": None,
        "tool_results": None,
    }


def run_rag_query(query: str, debug: bool = False) -> str:
    """
    Run the multi-agent RAG system for a query.

    Args:
        query: User's input query
        debug: Whether to print debug information

    Returns:
        Final agent response
    """

    print(f"\n{'='*70}")
    print(f"QUERY: {query}")
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
        print(f"RESPONSE")
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
            print(f"Documents Retrieved: {len(final_state.get('retrieved_documents', []))}")
            print(f"Retrieval Method: {final_state.get('retrieval_method', 'N/A')}")

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
    print("AGENTIC RAG SYSTEM - DEMO")
    print("="*70)

    # Sample queries demonstrating different capabilities
    demo_queries = [
        "What is retrieval augmented generation?",
        "How does semantic search work?",
        "Compare vector databases and keyword search",
        "What are embeddings used for?",
        "Tell me about llama",  # Unclear/ambiguous query
    ]

    for query in demo_queries:
        run_rag_query(query, debug=True)
        print("\n")


def interactive_mode():
    """
    Run in interactive mode, accepting user input.
    """

    print("\n" + "="*70)
    print("AGENTIC RAG SYSTEM - INTERACTIVE MODE")
    print("="*70)
    print("Enter 'quit' to exit, 'db' to check vector store status\n")

    # Check if vector store exists
    vector_store_path = Path(__file__).parent / "chroma_rag_db"
    if not vector_store_path.exists():
        print("WARNING: Vector store not found!")
        print("Please run: python vector_store_setup.py")
        print("Running setup now...\n")
        try:
            from vector_store_setup import setup_vector_store
            setup_vector_store()
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            return

    while True:
        try:
            query = input("\nYour question: ").strip()

            if query.lower() == "quit":
                print("Thank you for using the RAG system!")
                break

            if query.lower() == "db":
                if vector_store_path.exists():
                    print(f"✓ Vector store exists at: {vector_store_path}")
                    try:
                        from vector_store_setup import get_vector_store, print_collection_stats
                        vs = get_vector_store()
                        print_collection_stats(vs)
                    except Exception as e:
                        print(f"Could not retrieve stats: {str(e)}")
                else:
                    print("✗ Vector store not found")
                continue

            if not query:
                continue

            run_rag_query(query, debug=False)

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
            run_rag_query(query, debug=True)
    else:
        # Default: interactive mode
        interactive_mode()
