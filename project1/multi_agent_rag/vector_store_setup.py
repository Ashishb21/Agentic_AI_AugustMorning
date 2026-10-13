"""
Vector store setup for the agentic RAG system.
Handles document ingestion from web sources and Chroma vector store initialization.
"""

from pathlib import Path
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

# Vector store path
VECTOR_STORE_PATH = Path(__file__).parent / "chroma_rag_db"


def setup_vector_store() -> Chroma:
    """
    Set up the Chroma vector store with documents from web sources.

    Fetches articles about AI/ML topics from various sources, splits them
    into chunks, and creates a persistent Chroma vector store.

    Returns:
        Initialized Chroma vector store instance
    """
    print("\n[Vector Store Setup] Initializing Chroma vector store...")

    # URLs to ingest - Mix of official docs and educational content
    urls = [
        "https://python.langchain.com/docs/tutorials/rag/",
        "https://python.langchain.com/docs/concepts/retrieval/",
        "https://python.langchain.com/docs/integrations/vectorstores/chroma/",
        "https://langchain-ai.github.io/langgraph/",
        "https://blog.langchain.dev/tag/rag/",
    ]

    print(f"  Loading {len(urls)} web documents...")
    docs = []

    for url in urls:
        try:
            print(f"  - Fetching: {url}")
            loader = WebBaseLoader(url)
            loaded_docs = loader.load()
            docs.extend(loaded_docs)
            print(f"    ✓ Loaded {len(loaded_docs)} documents")
        except Exception as e:
            print(f"    ✗ Error loading {url}: {str(e)}")
            continue

    if not docs:
        print("  WARNING: No documents loaded from web. Using fallback documents.")
        docs = _create_fallback_documents()

    print(f"\n  Total documents loaded: {len(docs)}")

    # Split documents into chunks
    print("  Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"  Created {len(chunks)} chunks")

    # Create embeddings
    print("  Initializing embeddings model...")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    # Create Chroma vector store
    print(f"  Creating Chroma vector store at {VECTOR_STORE_PATH}...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_PATH),
        collection_name="rag_documents"
    )

    print("  ✓ Vector store created successfully!")

    # Print statistics
    print_collection_stats(vector_store)

    return vector_store


def get_vector_store() -> Chroma:
    """
    Get an existing Chroma vector store instance.

    Returns:
        Chroma vector store instance
    """
    if not VECTOR_STORE_PATH.exists():
        raise FileNotFoundError(
            f"Vector store not found at {VECTOR_STORE_PATH}. "
            "Please run: python vector_store_setup.py"
        )

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vector_store = Chroma(
        persist_directory=str(VECTOR_STORE_PATH),
        embedding_function=embeddings,
        collection_name="rag_documents"
    )

    return vector_store


def print_collection_stats(vector_store: Chroma) -> None:
    """
    Print statistics about the vector store collection.

    Args:
        vector_store: Chroma vector store instance
    """
    print("\n  Collection Statistics:")
    print(f"  ─────────────────────")

    # Get collection info
    collection = vector_store._collection
    count = collection.count()
    print(f"  Total documents: {count}")

    # Try to get sample metadata
    try:
        results = collection.get(limit=5)
        if results and results.get("documents"):
            print(f"  Sample documents: {len(results['documents'])}")
            if results.get("metadatas"):
                sources = set()
                for meta in results["metadatas"]:
                    if isinstance(meta, dict) and "source" in meta:
                        sources.add(meta["source"])
                if sources:
                    print(f"  Sources: {', '.join(list(sources)[:3])}")
    except Exception as e:
        print(f"  (Could not retrieve sample metadata: {str(e)})")

    print()


def _create_fallback_documents() -> List[Any]:
    """
    Create fallback documents if web loading fails.

    Returns:
        List of Document objects with sample content
    """
    from langchain_core.documents import Document

    fallback_docs = [
        Document(
            page_content="""
Retrieval-Augmented Generation (RAG) is a technique that combines document retrieval
with language model generation. It allows LLMs to access external knowledge bases,
improving accuracy and reducing hallucinations. RAG systems typically consist of:

1. A retriever that searches relevant documents
2. A generator that produces responses based on retrieved context

This approach is useful for Q&A systems, knowledge base querying, and fact-based tasks.
""",
            metadata={"source": "RAG_Overview"}
        ),
        Document(
            page_content="""
Vector databases store data as high-dimensional vectors (embeddings) and enable
efficient similarity search. Common vector databases include:

- Chroma: Lightweight, open-source vector database
- Weaviate: Production-ready vector database
- Pinecone: Cloud-hosted vector database
- FAISS: Facebook's similarity search library

Vector embeddings capture semantic meaning, allowing conceptual similarity matching
rather than just keyword matching.
""",
            metadata={"source": "Vector_Databases"}
        ),
        Document(
            page_content="""
LangGraph is a framework for building agent systems with explicit flow control.
It allows you to:

- Define stateful workflow graphs
- Route execution based on conditions
- Integrate LLMs with tools and external APIs
- Build multi-agent orchestration systems

LangGraph is particularly useful for building deterministic workflows that need
to coordinate multiple specialized agents.
""",
            metadata={"source": "LangGraph_Intro"}
        ),
        Document(
            page_content="""
Semantic search uses embeddings to find documents with similar meaning,
not just keyword matches. Unlike traditional keyword search:

- Semantic search understands context and intent
- It can find documents with different wording but same meaning
- It works well for conceptual queries
- Embedding models can be fine-tuned for domain-specific searches

Hybrid search combines semantic and keyword approaches for best results.
""",
            metadata={"source": "Semantic_Search"}
        ),
        Document(
            page_content="""
LangChain is a framework for developing applications powered by large language models.
Key components include:

- Document loaders: Fetch data from various sources
- Text splitters: Break documents into manageable chunks
- Embeddings: Convert text to vector representations
- Vector stores: Store and retrieve embeddings
- Chains: Combine components into workflows
- Agents: Give LLMs access to tools

LangChain simplifies the complexity of building LLM applications.
""",
            metadata={"source": "LangChain_Framework"}
        ),
    ]

    return fallback_docs


if __name__ == "__main__":
    # Setup vector store when script is run directly
    try:
        setup_vector_store()
        print("\n✓ Vector store setup complete!")
    except Exception as e:
        print(f"\n✗ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
