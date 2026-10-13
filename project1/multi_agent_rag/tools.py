"""
Retrieval tools for the agentic RAG system.
Provides document search capabilities with semantic and hybrid search options.
"""

from typing import Any, Dict, List
from langchain_core.tools import tool

try:
    from vector_store_setup import get_vector_store
except ImportError:
    from .vector_store_setup import get_vector_store


# ==================== HELPER FUNCTIONS ====================

def get_vector_store_instance():
    """Get Chroma vector store instance."""
    return get_vector_store()


def format_document(doc) -> dict:
    """
    Convert Document to dict with content and metadata.

    Args:
        doc: LangChain Document object

    Returns:
        Dictionary with content and metadata
    """
    return {
        "content": doc.page_content,
        "metadata": dict(doc.metadata) if hasattr(doc, "metadata") else {},
        "source": doc.metadata.get("source", "Unknown") if hasattr(doc, "metadata") else "Unknown"
    }


# ==================== RETRIEVAL TOOLS ====================

@tool
def semantic_search(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Perform semantic similarity search using embeddings.

    Finds documents based on semantic meaning and conceptual similarity.
    This works well for natural language queries and meaning-based searches.

    Args:
        query: Search query string (e.g., "What is RAG?")
        top_k: Number of top results to return (default: 5)

    Returns:
        Dictionary with 'found' key and results:
        - found: bool indicating if documents were found
        - documents: list of retrieved document chunks
        - scores: relevance scores for each document
    """
    try:
        vector_store = get_vector_store_instance()

        # Perform similarity search with scores
        search_results = vector_store.similarity_search_with_score(query, k=top_k)

        if not search_results:
            return {
                "found": False,
                "documents": [],
                "scores": [],
                "message": f"No documents found for query: {query}"
            }

        documents = []
        scores = []

        for doc, score in search_results:
            documents.append(format_document(doc))
            scores.append(float(score))

        return {
            "found": True,
            "documents": documents,
            "scores": scores,
            "count": len(documents)
        }

    except Exception as e:
        return {
            "found": False,
            "documents": [],
            "scores": [],
            "error": f"Semantic search failed: {str(e)}"
        }


@tool
def hybrid_search(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Perform hybrid search combining semantic similarity with diversity.

    Uses max marginal relevance (MMR) to balance relevance with document diversity.
    This prevents redundant results and provides more comprehensive coverage.

    Args:
        query: Search query string (e.g., "Compare RAG and standard LLM")
        top_k: Number of top results to return (default: 5)

    Returns:
        Dictionary with 'found' key and results:
        - found: bool indicating if documents were found
        - documents: list of retrieved document chunks
        - scores: relevance scores for each document
    """
    try:
        vector_store = get_vector_store_instance()

        # Perform max marginal relevance search
        search_results = vector_store.max_marginal_relevance_search_with_score(
            query,
            k=top_k,
            fetch_k=2 * top_k,  # Fetch more candidates for MMR
            lambda_mult=0.5  # Balance relevance vs diversity
        )

        if not search_results:
            return {
                "found": False,
                "documents": [],
                "scores": [],
                "message": f"No documents found for query: {query}"
            }

        documents = []
        scores = []

        for doc, score in search_results:
            documents.append(format_document(doc))
            scores.append(float(score))

        return {
            "found": True,
            "documents": documents,
            "scores": scores,
            "count": len(documents),
            "method": "hybrid_mmr"
        }

    except Exception as e:
        return {
            "found": False,
            "documents": [],
            "scores": [],
            "error": f"Hybrid search failed: {str(e)}"
        }


# ==================== TOOL COLLECTIONS ====================

RETRIEVAL_TOOLS = [semantic_search, hybrid_search]
ALL_TOOLS = RETRIEVAL_TOOLS
