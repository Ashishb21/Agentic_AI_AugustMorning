"""RAG pieces used by the FastAPI routes in main.py.

The vector store is persisted on disk, so ingestion happens only when you call
one of the ingest_* helpers -- importing this module does NOT re-embed anything.
"""

import os
import tempfile

import bs4
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "qwen3-embedding")
PERSIST_DIR = os.getenv("PERSIST_DIR", "./chroma_db_1")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_demo")
TOP_K = int(os.getenv("TOP_K", "4"))

llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)

# Opens the collection on disk, creating it empty the first time.
vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

retriever = vectorstore.as_retriever(
    search_type="similarity",  # or "mmr" for diversity
    search_kwargs={"k": TOP_K},
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True,  # records char offset in metadata
)

prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the question using ONLY the context below.
If the context does not contain the answer, say you don't know. Keep it to three sentences.

Context:
{context}

Question: {question}

Answer:"""
)

answer_chain = prompt | llm | StrOutputParser()


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(d.page_content for d in docs)


def doc_count() -> int:
    """How many chunks are currently stored."""
    return vectorstore._collection.count()


def _add(docs: list[Document]) -> int:
    chunks = splitter.split_documents(docs)
    if not chunks:
        return 0
    vectorstore.add_documents(chunks)
    return len(chunks)


def ingest_url(url: str) -> int:
    """Scrape a page and add it to the vector store. Returns chunks added."""
    loader = WebBaseLoader(
        web_paths=[url],
        bs_kwargs={
            "parse_only": bs4.SoupStrainer(
                class_=("post-content", "post-title", "post-header")
            )
        },
    )
    docs = loader.load()
    # Some pages have none of those CSS classes -- fall back to the whole page.
    if not any(d.page_content.strip() for d in docs):
        docs = WebBaseLoader(web_paths=[url]).load()
    return _add(docs)


def ingest_text(text: str, source: str = "inline") -> int:
    return _add([Document(page_content=text, metadata={"source": source})])


def ingest_pdf_bytes(data: bytes, filename: str) -> int:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        docs = PyPDFLoader(tmp_path).load()
        for d in docs:
            d.metadata["source"] = filename
        return _add(docs)
    finally:
        os.unlink(tmp_path)


def rag_chat(query: str, k: int | None = None) -> dict:
    """Retrieve, then answer. Returns the answer plus the sources used."""
    docs = retriever.invoke(query) if k is None else vectorstore.similarity_search(query, k=k)
    if not docs:
        return {
            "answer": "The knowledge base is empty. Ingest a document first.",
            "sources": [],
        }
    answer = answer_chain.invoke({"context": format_docs(docs), "question": query})
    sources = [
        {
            "source": d.metadata.get("source", "unknown"),
            "start_index": d.metadata.get("start_index"),
            "snippet": d.page_content[:200],
        }
        for d in docs
    ]
    return {"answer": answer, "sources": sources}


def reset() -> int:
    """Drop every chunk and recreate an empty collection. Returns chunks removed.

    reset_collection() recreates the collection on the same object, so the
    module-level `vectorstore` / `retriever` stay valid afterwards.
    """
    removed = doc_count()
    vectorstore.reset_collection()
    return removed
