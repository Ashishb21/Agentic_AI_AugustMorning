"""FastAPI routes for the RAG demo.

Run with:  uvicorn main:app --reload
Docs at:   http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

import app1.rag_service as rag_service

app = FastAPI(title="RAG Demo", version="1.0")


class Userquery(BaseModel):
    query: str
    user_id: int = 0
    k: int | None = None


class UrlIngest(BaseModel):
    url: str


class TextIngest(BaseModel):
    text: str
    source: str = "inline"


class ResetRequest(BaseModel):
    confirm: bool = False


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm": rag_service.LLM_MODEL,
        "embed_model": rag_service.EMBED_MODEL,
        "collection": rag_service.COLLECTION_NAME,
        "chunks": rag_service.doc_count(),
    }


@app.post("/ingest/url")
async def ingest_url(body: UrlIngest):
    try:
        added = rag_service.ingest_url(body.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not load {body.url}: {exc}")
    return {"url": body.url, "chunks_added": added, "total_chunks": rag_service.doc_count()}


@app.post("/ingest/text")
async def ingest_text(body: TextIngest):
    added = rag_service.ingest_text(body.text, body.source)
    return {"source": body.source, "chunks_added": added, "total_chunks": rag_service.doc_count()}


@app.post("/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are supported")
    added = rag_service.ingest_pdf_bytes(await file.read(), file.filename)
    return {"file": file.filename, "chunks_added": added, "total_chunks": rag_service.doc_count()}


@app.post("/rag-chat")
async def rag_chat(user: Userquery):
    if not user.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")
    result = rag_service.rag_chat(user.query, user.k)
    return {"user_id": user.user_id, "query": user.query, **result}


@app.post("/reset")
async def reset(body: ResetRequest):
    """Wipe the vector store. Irreversible -- requires {"confirm": true}."""
    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail='Refusing to wipe the collection. Send {"confirm": true} to proceed.',
        )
    removed = rag_service.reset()
    return {"chunks_removed": removed, "total_chunks": rag_service.doc_count()}
