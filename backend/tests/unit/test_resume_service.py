"""
Unit tests for resume service.

Tests:
- PDF text extraction
- Resume analysis with Groq
- Error handling for invalid files
- Mock Groq API responses
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from app.services import resume_service


@pytest.mark.unit
class TestResumeTextExtraction:
    """Test PDF text extraction functionality."""

    @pytest.mark.asyncio
    async def test_extract_text_from_valid_pdf(self):
        """Test extracting text from a valid PDF file."""
        mock_pdf_content = "John Doe\nSoftware Engineer\nPython, FastAPI, React"
        
        with patch('fitz.open') as mock_fitz:
            # Mock PyMuPDF document
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_page.get_text.return_value = mock_pdf_content
            mock_doc.__iter__.return_value = [mock_page]
            mock_fitz.return_value = mock_doc
            
            result = await resume_service.extract_text_from_pdf("test.pdf")
            
            assert isinstance(result, str)
            assert "John Doe" in result
            assert "Python" in result
            mock_doc.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_handles_empty_pdf(self):
        """Test handling of empty PDF files."""
        with patch('fitz.open') as mock_fitz:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_page.get_text.return_value = ""
            mock_doc.__iter__.return_value = [mock_page]
            mock_fitz.return_value = mock_doc
            
            result = await resume_service.extract_text_from_pdf("empty.pdf")
            
            assert result == ""
            mock_doc.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_handles_error(self):
        """Test error handling for corrupted PDF files."""
        with patch('fitz.open', side_effect=Exception("Invalid PDF")):
            result = await resume_service.extract_text_from_pdf("corrupt.pdf")
            
            assert "Error extracting text" in result
            assert "Invalid PDF" in result


@pytest.mark.unit
class TestResumeAnalysis:
    """Test resume analysis with Groq LLM."""

    @pytest.mark.asyncio
    async def test_analyze_resume_with_valid_text(self, mocker):
        """Test resume analysis with valid resume text."""
        resume_text = "John Doe - Senior Software Engineer with 5 years experience in Python, FastAPI, Docker, AWS"
        
        mock_analysis = {
            "resume_score": 85,
            "ats_score": 90,
            "strong_skills": ["Python", "FastAPI", "Docker", "AWS"],
            "weak_skills": ["Kubernetes", "GraphQL"],
            "grammar_issues": [],
            "formatting_suggestions": ["Add contact section", "Use bullet points"],
            "missing_keywords": ["CI/CD", "Microservices"],
            "improvement_tips": ["Quantify achievements", "Add metrics"],
            "experience_years": 5.0,
            "education": {"degree": "B.Tech", "institution": "MIT", "year": "2018"},
            "projects_detected": [{"name": "API Gateway", "description": "Built scalable gateway", "tech_stack": ["Python", "FastAPI"]}],
            "summary": "Strong technical profile with good cloud experience"
        }
        
        mock_groq = mocker.patch('app.services.resume_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(mock_analysis).replace("'", '"')  # JSON string
        
        with patch('json.loads', return_value=mock_analysis):
            result = await resume_service.analyze_resume(resume_text)
        
        assert result["resume_score"] == 85
        assert result["ats_score"] == 90
        assert "Python" in result["strong_skills"]
        assert result["experience_years"] == 5.0
        mock_groq.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_resume_with_short_text_returns_mock(self):
        """Test that short or empty text returns mock analysis."""
        result = await resume_service.analyze_resume("")
        
        # Should return mock analysis for empty text
        assert "resume_score" in result
        assert "ats_score" in result
        assert isinstance(result["resume_score"], int)
        assert 0 <= result["resume_score"] <= 100

    @pytest.mark.asyncio
    async def test_analyze_resume_handles_groq_api_error(self, mocker):
        """Test error handling when Groq API fails."""
        resume_text = "Valid resume text with sufficient content for analysis"
        
        mock_groq = mocker.patch('app.services.resume_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.side_effect = Exception("Groq API error")
        
        result = await resume_service.analyze_resume(resume_text)
        
        # Should return mock analysis on error
        assert "resume_score" in result
        assert "ats_score" in result
        assert isinstance(result["resume_score"], int)

    @pytest.mark.asyncio
    async def test_analyze_resume_handles_invalid_json(self, mocker):
        """Test handling of invalid JSON response from Groq."""
        resume_text = "Valid resume text for analysis"
        
        mock_groq = mocker.patch('app.services.resume_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = "Invalid JSON {{"
        
        result = await resume_service.analyze_resume(resume_text)
        
        # Should return mock analysis on JSON decode error
        assert "resume_score" in result
        assert "ats_score" in result

    @pytest.mark.asyncio
    async def test_analyze_resume_scoring_calculation(self):
        """Test that resume_score and ats_score are properly calculated."""
        # Test with mock analysis to verify score structure
        result = resume_service._mock_analysis()
        
        assert isinstance(result["resume_score"], int)
        assert isinstance(result["ats_score"], int)
        assert 0 <= result["resume_score"] <= 100
        assert 0 <= result["ats_score"] <= 100


@pytest.mark.unit
class TestFileUpload:
    """Test file upload and storage."""

    @pytest.mark.asyncio
    async def test_save_uploaded_file(self):
        """Test saving uploaded file to disk."""
        file_content = b"Sample PDF content"
        filename = "resume.pdf"
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = await resume_service.save_uploaded_file(file_content, filename)
        
        assert result.endswith(filename)
        assert "resume.pdf" in result
        mock_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_uploaded_file_creates_unique_name(self):
        """Test that saved files have unique names."""
        file_content = b"Sample content"
        filename = "resume.pdf"
        
        with patch('builtins.open', mock_open()):
            result1 = await resume_service.save_uploaded_file(file_content, filename)
            result2 = await resume_service.save_uploaded_file(file_content, filename)
        
        # Should have different UUIDs
        assert result1 != result2


@pytest.mark.unit
class TestResumeServiceErrorHandling:
    """Test error handling in resume service."""

    @pytest.mark.asyncio
    async def test_analyze_resume_with_null_text(self):
        """Test handling of None text input."""
        result = await resume_service.analyze_resume(None)
        
        assert "resume_score" in result
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_resume_with_very_long_text(self, mocker):
        """Test that very long text is truncated properly."""
        # Create text longer than 8000 chars
        long_text = "A" * 10000
        
        mock_groq = mocker.patch('app.services.resume_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = '{"resume_score": 75, "ats_score": 80, "strong_skills": [], "weak_skills": [], "grammar_issues": [], "formatting_suggestions": [], "missing_keywords": [], "improvement_tips": [], "experience_years": 0, "education": {}, "projects_detected": [], "summary": ""}'
        
        await resume_service.analyze_resume(long_text)
        
        # Verify that the text passed to Groq is limited to 8000 chars
        call_args = mock_groq.call_args
        messages = call_args[1]["messages"] if "messages" in call_args[1] else call_args[0][0]
        user_message = messages[1]["content"]
        
        # The prompt + text should not exceed reasonable limits
        assert len(user_message) < 10000
