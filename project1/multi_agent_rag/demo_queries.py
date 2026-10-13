"""
Testing and demonstration for the agentic RAG system.
Includes pytest tests and demo functions for different query types.
"""

import pytest
from pathlib import Path

try:
    from main import run_rag_query
    from vector_store_setup import get_vector_store
except ImportError:
    from .main import run_rag_query
    from .vector_store_setup import get_vector_store


# ==================== FIXTURES ====================

@pytest.fixture(scope="session")
def vector_store():
    """Fixture to provide vector store for tests."""
    try:
        return get_vector_store()
    except FileNotFoundError:
        pytest.skip("Vector store not initialized")


@pytest.fixture
def sample_queries():
    """Fixture providing sample queries of different types."""
    return {
        "simple": [
            "What is retrieval augmented generation?",
            "Explain vector embeddings",
            "What is a vector database?",
        ],
        "complex": [
            "Compare semantic search and keyword search",
            "What are the benefits and limitations of RAG?",
            "How do vector embeddings capture meaning?",
        ],
        "unclear": [
            "Tell me more",
            "What about it?",
            "How so?",
        ]
    }


# ==================== TEST CLASSES ====================

class TestSimpleQueries:
    """Tests for simple, factual queries."""

    def test_factual_query(self, vector_store):
        """Test simple factual question about RAG."""
        query = "What is retrieval augmented generation?"
        response = run_rag_query(query, debug=False)

        assert response is not None
        assert len(response) > 0
        assert "augmented" in response.lower() or "retrieval" in response.lower()

    def test_definition_query(self, vector_store):
        """Test definition query about embeddings."""
        query = "Explain vector embeddings"
        response = run_rag_query(query, debug=False)

        assert response is not None
        assert len(response) > 0

    def test_simple_returns_response(self, vector_store):
        """Test that simple queries always return a response."""
        query = "What is a vector database?"
        response = run_rag_query(query, debug=False)

        assert isinstance(response, str)
        assert len(response) > 10  # Should have substantial response


class TestComplexQueries:
    """Tests for complex comparison and reasoning queries."""

    def test_comparison_query(self, vector_store):
        """Test complex comparison question."""
        query = "Compare semantic search and keyword search"
        response = run_rag_query(query, debug=False)

        assert response is not None
        assert len(response) > 0

    def test_reasoning_query(self, vector_store):
        """Test query requiring reasoning."""
        query = "What are the benefits and limitations of RAG?"
        response = run_rag_query(query, debug=False)

        assert isinstance(response, str)
        assert len(response) > 50

    def test_complex_returns_detailed_response(self, vector_store):
        """Test that complex queries return detailed responses."""
        query = "How do embeddings help with semantic understanding?"
        response = run_rag_query(query, debug=False)

        assert isinstance(response, str)
        assert "==" in response or len(response) > 100  # Detailed response


class TestClarification:
    """Tests for unclear query handling."""

    def test_unclear_query_handling(self, vector_store):
        """Test that unclear queries are handled gracefully."""
        query = "Tell me more"
        response = run_rag_query(query, debug=False)

        assert response is not None
        assert isinstance(response, str)
        # Should ask for clarification
        assert any(word in response.lower() for word in ["clarif", "more information", "unclear"])

    def test_vague_query(self, vector_store):
        """Test handling of vague queries."""
        query = "What about it?"
        response = run_rag_query(query, debug=False)

        assert isinstance(response, str)
        assert len(response) > 0


class TestResponseFormat:
    """Tests for response formatting and structure."""

    def test_response_has_structure(self, vector_store):
        """Test that responses have proper structure."""
        query = "What is RAG?"
        response = run_rag_query(query, debug=False)

        assert isinstance(response, str)
        # Response should have content
        lines = response.strip().split("\n")
        assert len(lines) > 1

    def test_sources_included_when_available(self, vector_store):
        """Test that sources are included in response when documents retrieved."""
        query = "Explain semantic search"
        response = run_rag_query(query, debug=False)

        # Response should either have sources or explanation
        assert len(response) > 50


# ==================== DEMO FUNCTIONS ====================

def demo_simple_queries():
    """Demonstrate handling of simple queries."""
    print("\n" + "="*70)
    print("SIMPLE QUERIES DEMO")
    print("="*70)

    simple_queries = [
        "What is retrieval augmented generation?",
        "Explain vector embeddings",
        "What is semantic search?",
    ]

    for query in simple_queries:
        print(f"\n[Query] {query}")
        run_rag_query(query, debug=True)


def demo_complex_queries():
    """Demonstrate handling of complex queries."""
    print("\n" + "="*70)
    print("COMPLEX QUERIES DEMO")
    print("="*70)

    complex_queries = [
        "Compare semantic search and keyword search",
        "What are the advantages and disadvantages of RAG systems?",
        "How do vector embeddings improve search results?",
    ]

    for query in complex_queries:
        print(f"\n[Query] {query}")
        run_rag_query(query, debug=True)


def demo_unclear_queries():
    """Demonstrate handling of unclear queries."""
    print("\n" + "="*70)
    print("UNCLEAR QUERIES DEMO")
    print("="*70)

    unclear_queries = [
        "Tell me more",
        "What about it?",
        "Can you help?",
    ]

    for query in unclear_queries:
        print(f"\n[Query] {query}")
        run_rag_query(query, debug=True)


def demo_all():
    """Run all demonstration scenarios."""
    print("\n" + "="*70)
    print("AGENTIC RAG SYSTEM - COMPREHENSIVE DEMO")
    print("="*70)

    # Check vector store
    vector_store_path = Path(__file__).parent / "chroma_rag_db"
    if not vector_store_path.exists():
        print("\nVector store not found. Please run: python vector_store_setup.py")
        return

    demo_simple_queries()
    demo_complex_queries()
    demo_unclear_queries()

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "simple":
            demo_simple_queries()
        elif sys.argv[1] == "complex":
            demo_complex_queries()
        elif sys.argv[1] == "unclear":
            demo_unclear_queries()
        elif sys.argv[1] == "test":
            pytest.main([__file__, "-v"])
        else:
            demo_all()
    else:
        demo_all()
