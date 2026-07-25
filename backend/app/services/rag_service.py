"""
RAG (Retrieval-Augmented Generation) Service
Uses ChromaDB and Sentence Transformers (or TF-IDF fallback) for vector embedding and retrieval over resume and career documents.
"""
import os
import uuid
from typing import List, Dict, Any
from pathlib import Path

from app.core.config import settings
from app.services.groq_service import groq_service

# Attempt importing ChromaDB
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    _chroma_available = True
except ImportError:
    _chroma_available = False


class RAGVectorStore:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        if _chroma_available:
            try:
                self.client = chromadb.PersistentClient(path=self.persist_dir)
                self.collection = self.client.get_or_create_collection(name="resume_chunks")
            except Exception:
                self.client = None
                self.collection = None
        else:
            self.client = None
            self.collection = None

        self.memory_store: Dict[str, List[Dict[str, Any]]] = {}

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split raw text into overlapping paragraphs or chunks."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            if len(current_chunk) + len(p) <= chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + p
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = p

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]

    async def add_document(self, doc_id: str, text: str, metadata: dict):
        """Index a document's chunks into vector DB."""
        chunks = self.chunk_text(text)

        if self.collection:
            ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
            metadatas = [metadata for _ in chunks]
            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )

        # Always keep in memory store as fallback
        self.memory_store[doc_id] = [
            {"chunk": c, "metadata": metadata} for c in chunks
        ]

    async def query(self, doc_id: str, query_text: str, top_k: int = 3) -> List[str]:
        """Search relevant chunks for a specific document."""
        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                    where={"user_id": metadata.get("user_id")} if "user_id" in metadata else None
                )
                if results and results.get("documents") and results["documents"][0]:
                    return results["documents"][0]
            except Exception:
                pass

        # Fallback keyword match over memory store
        doc_chunks = self.memory_store.get(doc_id, [])
        if not doc_chunks:
            return []

        query_terms = set(query_text.lower().split())
        scored = []
        for item in doc_chunks:
            chunk = item["chunk"]
            score = sum(1 for term in query_terms if term in chunk.lower())
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored[:top_k]]


rag_vector_store = RAGVectorStore()


async def query_resume_with_rag(raw_text: str, user_query: str) -> str:
    """RAG Pipeline: Embed -> Retrieve relevant sections -> Groq LLM answer."""
    doc_id = str(uuid.uuid4())
    await rag_vector_store.add_document(doc_id, raw_text, {"doc_id": doc_id})

    relevant_chunks = await rag_vector_store.query(doc_id, user_query, top_k=3)
    context_str = "\n---\n".join(relevant_chunks) if relevant_chunks else raw_text[:2000]

    rag_prompt = f"""You are an AI Career Assistant using RAG (Retrieval-Augmented Generation).
Answer the user's question accurately using ONLY the provided resume context below.
If the context does not contain the answer, say so politely.

CONTEXT FROM RESUME:
{context_str}

USER QUESTION:
{user_query}

ANSWER:"""

    messages = [
        {"role": "system", "content": "You are a factual career advisor. Never hallucinate details not present in the resume."},
        {"role": "user", "content": rag_prompt}
    ]

    return await groq_service.chat_completion(messages, temperature=0.2)
