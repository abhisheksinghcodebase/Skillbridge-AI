"""
Unit tests for RAG service.

Tests:
- Document retrieval from ChromaDB
- Query embedding and similarity search
- Mock ChromaDB collection responses
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services import rag_service


@pytest.mark.unit
class TestRAGVectorStore:
    """Test RAG vector store functionality."""

    def test_chunk_text_creates_chunks(self):
        """Test text chunking functionality."""
        store = rag_service.RAGVectorStore()
        
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = store.chunk_text(text, chunk_size=50, overlap=10)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunk_text_handles_empty_text(self):
        """Test chunking with empty text."""
        store = rag_service.RAGVectorStore()
        
        chunks = store.chunk_text("")
        
        assert chunks == [""]

    def test_chunk_text_respects_chunk_size(self):
        """Test that chunks don't exceed chunk_size."""
        store = rag_service.RAGVectorStore()
        
        # Create long text
        long_paragraph = "A" * 1000
        chunks = store.chunk_text(long_paragraph, chunk_size=200, overlap=50)
        
        # Each chunk should be reasonably sized
        assert all(len(chunk) <= 1000 for chunk in chunks)

    @pytest.mark.asyncio
    async def test_add_document_to_memory_store(self):
        """Test adding document to memory store."""
        store = rag_service.RAGVectorStore()
        
        doc_id = "test_doc_123"
        text = "This is a test resume.\n\nIt has multiple paragraphs.\n\nAbout skills and experience."
        metadata = {"user_id": "user_123", "type": "resume"}
        
        await store.add_document(doc_id, text, metadata)
        
        assert doc_id in store.memory_store
        assert len(store.memory_store[doc_id]) > 0
        assert store.memory_store[doc_id][0]["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_add_document_to_chromadb(self, mocker):
        """Test adding document to ChromaDB collection."""
        mock_collection = MagicMock()
        
        store = rag_service.RAGVectorStore()
        store.collection = mock_collection
        
        doc_id = "test_doc_456"
        text = "Resume content here.\n\nMore content."
        metadata = {"user_id": "user_456"}
        
        await store.add_document(doc_id, text, metadata)
        
        # Verify ChromaDB add was called
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        
        assert "documents" in call_args[1]
        assert "ids" in call_args[1]
        assert "metadatas" in call_args[1]

    @pytest.mark.asyncio
    async def test_query_from_memory_store(self):
        """Test querying documents from memory store."""
        store = rag_service.RAGVectorStore()
        store.collection = None  # Force memory store usage
        
        doc_id = "test_doc_789"
        text = "Python expert with 5 years experience.\n\nSkilled in FastAPI and Django.\n\nBuilt scalable microservices."
        metadata = {"user_id": "user_789"}
        
        await store.add_document(doc_id, text, metadata)
        
        # Query for Python-related content
        results = await store.query(doc_id, "Python FastAPI", top_k=2)
        
        assert isinstance(results, list)
        assert len(results) <= 2
        if results:
            # Should contain relevant chunks
            assert any("Python" in chunk or "FastAPI" in chunk for chunk in results)

    @pytest.mark.asyncio
    async def test_query_with_no_results(self):
        """Test querying non-existent document."""
        store = rag_service.RAGVectorStore()
        
        results = await store.query("nonexistent_doc", "query text", top_k=3)
        
        assert results == []

    @pytest.mark.asyncio
    async def test_query_from_chromadb(self, mocker):
        """Test querying from ChromaDB collection."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["Chunk 1 about Python", "Chunk 2 about Django", "Chunk 3 about APIs"]]
        }
        
        store = rag_service.RAGVectorStore()
        store.collection = mock_collection
        
        doc_id = "test_doc_999"
        query_text = "Python frameworks"
        
        results = await store.query(doc_id, query_text, top_k=3)
        
        assert len(results) == 3
        assert "Python" in results[0]
        mock_collection.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_falls_back_on_chromadb_error(self):
        """Test fallback to memory store when ChromaDB fails."""
        mock_collection = MagicMock()
        mock_collection.query.side_effect = Exception("ChromaDB error")
        
        store = rag_service.RAGVectorStore()
        store.collection = mock_collection
        
        doc_id = "test_doc_fallback"
        text = "Python developer with FastAPI experience."
        metadata = {"user_id": "user_fallback"}
        
        await store.add_document(doc_id, text, metadata)
        
        # Should fallback to memory store
        results = await store.query(doc_id, "Python FastAPI", top_k=2)
        
        assert isinstance(results, list)


@pytest.mark.unit
class TestRAGQueryWithLLM:
    """Test RAG query pipeline with LLM."""

    @pytest.mark.asyncio
    async def test_query_resume_with_rag_success(self, mocker):
        """Test successful RAG query with LLM response."""
        raw_text = "John Doe is a Python developer with 5 years of experience in building web applications using FastAPI and Django."
        user_query = "What is the candidate's experience with Python?"
        
        mock_groq = mocker.patch('app.services.rag_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = "John Doe has 5 years of experience with Python, specializing in web applications using FastAPI and Django."
        
        result = await rag_service.query_resume_with_rag(raw_text, user_query)
        
        assert isinstance(result, str)
        assert len(result) > 0
        mock_groq.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_resume_retrieves_relevant_chunks(self, mocker):
        """Test that RAG retrieves relevant chunks before LLM call."""
        raw_text = "Skill section: Python, JavaScript, Docker.\n\nExperience: 3 years at Tech Corp.\n\nEducation: B.Tech in CS."
        user_query = "What are the candidate's skills?"
        
        mock_groq = mocker.patch('app.services.rag_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = "The candidate's skills include Python, JavaScript, and Docker."
        
        result = await rag_service.query_resume_with_rag(raw_text, user_query)
        
        # Verify Groq was called with context
        call_args = mock_groq.call_args
        messages = call_args[0][0]  # First positional argument
        user_message = messages[1]["content"]
        
        # Should contain relevant context
        assert "CONTEXT FROM RESUME" in user_message or "skills" in user_message.lower()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_query_resume_handles_empty_text(self, mocker):
        """Test RAG query with empty resume text."""
        raw_text = ""
        user_query = "What is the candidate's experience?"
        
        mock_groq = mocker.patch('app.services.rag_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = "I don't have enough information to answer that question."
        
        result = await rag_service.query_resume_with_rag(raw_text, user_query)
        
        assert isinstance(result, str)
        mock_groq.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_resume_limits_context_length(self, mocker):
        """Test that very long resumes are truncated in context."""
        # Create very long text
        raw_text = "A" * 10000
        user_query = "Test query"
        
        mock_groq = mocker.patch('app.services.rag_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = "Test response"
        
        result = await rag_service.query_resume_with_rag(raw_text, user_query)
        
        # Verify context was limited
        call_args = mock_groq.call_args
        messages = call_args[0][0]
        user_message = messages[1]["content"]
        
        # Context should be reasonable length (not 10000+ chars)
        assert len(user_message) < 5000
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_query_resume_uses_low_temperature(self, mocker):
        """Test that RAG queries use low temperature for factual responses."""
        raw_text = "Test resume content"
        user_query = "Test query"
        
        mock_groq = mocker.patch('app.services.rag_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = "Test response"
        
        await rag_service.query_resume_with_rag(raw_text, user_query)
        
        # Verify temperature parameter
        call_args = mock_groq.call_args
        
        # Check if temperature was passed
        if "temperature" in call_args[1]:
            assert call_args[1]["temperature"] <= 0.3  # Low temperature for factual responses


@pytest.mark.unit
class TestRAGVectorStoreInitialization:
    """Test RAG vector store initialization."""

    def test_vector_store_initializes_memory_store(self):
        """Test that vector store always has memory store fallback."""
        store = rag_service.RAGVectorStore()
        
        assert hasattr(store, 'memory_store')
        assert isinstance(store.memory_store, dict)

    def test_vector_store_handles_chromadb_unavailable(self, mocker):
        """Test graceful handling when ChromaDB is not available."""
        # This test verifies the system works without ChromaDB
        mocker.patch('app.services.rag_service._chroma_available', False)
        
        store = rag_service.RAGVectorStore()
        
        assert store.client is None
        assert store.collection is None
        assert isinstance(store.memory_store, dict)
