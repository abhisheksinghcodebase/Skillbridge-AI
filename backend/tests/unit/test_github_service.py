"""
Unit tests for GitHub service.

Tests:
- GitHub profile analysis with mock API responses
- Repository analysis and commit history parsing
- Error handling for invalid usernames
- Mock httpx responses for GitHub API
"""
import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.services import github_service


@pytest.mark.unit
class TestGitHubDataFetching:
    """Test GitHub API data fetching."""

    @pytest.mark.asyncio
    async def test_fetch_github_data_with_valid_username(self, mocker):
        """Test fetching GitHub data for a valid username."""
        username = "testuser"
        
        mock_user_data = {
            "login": username,
            "name": "Test User",
            "bio": "Software Developer",
            "public_repos": 15,
            "followers": 50,
            "following": 30
        }
        
        mock_repos_data = [
            {
                "name": "awesome-project",
                "description": "An awesome project",
                "stargazers_count": 100,
                "language": "Python",
                "html_url": "https://github.com/testuser/awesome-project"
            },
            {
                "name": "another-repo",
                "description": "Another repository",
                "stargazers_count": 50,
                "language": "JavaScript",
                "html_url": "https://github.com/testuser/another-repo"
            }
        ]
        
        mock_client = AsyncMock()
        mock_user_response = AsyncMock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = mock_user_data
        
        mock_repos_response = AsyncMock()
        mock_repos_response.status_code = 200
        mock_repos_response.json.return_value = mock_repos_data
        
        mock_client.get = AsyncMock(side_effect=[mock_user_response, mock_repos_response])
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await github_service.fetch_github_data(username)
        
        assert "user" in result
        assert "repos" in result
        assert result["user"]["login"] == username
        assert len(result["repos"]) == 2

    @pytest.mark.asyncio
    async def test_fetch_github_data_with_invalid_username(self, mocker):
        """Test error handling for invalid GitHub username."""
        username = "nonexistentuser123456789"
        
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await github_service.fetch_github_data(username)
        
        assert "error" in result
        assert username in result["error"]

    @pytest.mark.asyncio
    async def test_fetch_github_data_uses_token_if_available(self, mocker):
        """Test that GitHub token is used in headers when available."""
        username = "testuser"
        
        mock_settings = mocker.patch('app.services.github_service.settings')
        mock_settings.GITHUB_TOKEN = "test_token_123"
        
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": username}
        
        mock_repos_response = AsyncMock()
        mock_repos_response.status_code = 200
        mock_repos_response.json.return_value = []
        
        mock_client.get = AsyncMock(side_effect=[mock_response, mock_repos_response])
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            await github_service.fetch_github_data(username)
        
        # Verify token was included in headers
        call_args = mock_client.get.call_args_list[0]
        headers = call_args[1]["headers"]
        assert "Authorization" in headers
        assert "test_token_123" in headers["Authorization"]

    @pytest.mark.asyncio
    async def test_fetch_github_data_handles_network_error(self, mocker):
        """Test handling of network errors when fetching GitHub data."""
        username = "testuser"
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await github_service.fetch_github_data(username)
        
        assert "error" in result


@pytest.mark.unit
class TestGitHubProfileAnalysis:
    """Test GitHub profile analysis functionality."""

    @pytest.mark.asyncio
    async def test_analyze_github_profile_success(self, mocker):
        """Test successful GitHub profile analysis."""
        username = "testuser"
        
        mock_github_data = {
            "user": {
                "name": "Test User",
                "bio": "Developer",
                "public_repos": 10,
                "followers": 25,
                "following": 15
            },
            "repos": [
                {
                    "name": "project1",
                    "description": "First project",
                    "stargazers_count": 10,
                    "language": "Python",
                    "html_url": "https://github.com/testuser/project1"
                }
            ]
        }
        
        mock_fetch = mocker.patch('app.services.github_service.fetch_github_data', new_callable=AsyncMock)
        mock_fetch.return_value = mock_github_data
        
        mock_analysis = {
            "overall_score": 75,
            "strengths": ["Good Python skills"],
            "weaknesses": ["Few repos"],
            "suggestions": [],
            "missing_aspects": [],
            "profile_grade": "B",
            "career_readiness": "almost_ready",
            "summary": "Good profile"
        }
        
        mock_groq = mocker.patch('app.services.github_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(mock_analysis).replace("'", '"')
        
        import json
        with mocker.patch('json.loads', return_value=mock_analysis):
            result = await github_service.analyze_github_profile(username)
        
        assert "username" in result
        assert result["username"] == username
        assert "ai_analysis" in result
        assert result["ai_analysis"]["overall_score"] == 75

    @pytest.mark.asyncio
    async def test_analyze_github_profile_computes_language_stats(self, mocker):
        """Test that language statistics are computed correctly."""
        username = "testuser"
        
        mock_github_data = {
            "user": {"name": "Test", "public_repos": 5},
            "repos": [
                {"language": "Python", "stargazers_count": 10, "description": "Project 1"},
                {"language": "Python", "stargazers_count": 5, "description": "Project 2"},
                {"language": "JavaScript", "stargazers_count": 3, "description": "Project 3"},
                {"language": "Python", "stargazers_count": 2, "description": "Project 4"},
                {"language": None, "stargazers_count": 0, "description": "Project 5"}
            ]
        }
        
        mock_fetch = mocker.patch('app.services.github_service.fetch_github_data', new_callable=AsyncMock)
        mock_fetch.return_value = mock_github_data
        
        mock_groq = mocker.patch('app.services.github_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(github_service._mock_github_analysis()).replace("'", '"')
        
        import json
        with mocker.patch('json.loads', return_value=github_service._mock_github_analysis()):
            result = await github_service.analyze_github_profile(username)
        
        # Python should be top language (3 repos)
        assert "top_languages" in result
        assert len(result["top_languages"]) >= 1
        assert result["top_languages"][0]["language"] == "Python"
        assert result["top_languages"][0]["repos"] == 3

    @pytest.mark.asyncio
    async def test_analyze_github_profile_calculates_total_stars(self, mocker):
        """Test that total stars are calculated correctly."""
        username = "testuser"
        
        mock_github_data = {
            "user": {"name": "Test", "public_repos": 3},
            "repos": [
                {"language": "Python", "stargazers_count": 100, "description": "A"},
                {"language": "Python", "stargazers_count": 50, "description": "B"},
                {"language": "Python", "stargazers_count": 25, "description": "C"}
            ]
        }
        
        mock_fetch = mocker.patch('app.services.github_service.fetch_github_data', new_callable=AsyncMock)
        mock_fetch.return_value = mock_github_data
        
        mock_groq = mocker.patch('app.services.github_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(github_service._mock_github_analysis()).replace("'", '"')
        
        import json
        with mocker.patch('json.loads', return_value=github_service._mock_github_analysis()):
            result = await github_service.analyze_github_profile(username)
        
        assert result["total_stars"] == 175  # 100 + 50 + 25

    @pytest.mark.asyncio
    async def test_analyze_github_profile_handles_fetch_error(self, mocker):
        """Test handling of errors when fetching GitHub data fails."""
        username = "testuser"
        
        mock_fetch = mocker.patch('app.services.github_service.fetch_github_data', new_callable=AsyncMock)
        mock_fetch.return_value = {"error": "User not found"}
        
        result = await github_service.analyze_github_profile(username)
        
        assert "error" in result
        assert "User not found" in result["error"]

    @pytest.mark.asyncio
    async def test_analyze_github_profile_handles_groq_error(self, mocker):
        """Test that Groq API errors fall back to mock analysis."""
        username = "testuser"
        
        mock_github_data = {
            "user": {"name": "Test", "public_repos": 5},
            "repos": []
        }
        
        mock_fetch = mocker.patch('app.services.github_service.fetch_github_data', new_callable=AsyncMock)
        mock_fetch.return_value = mock_github_data
        
        mock_groq = mocker.patch('app.services.github_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.side_effect = Exception("Groq API error")
        
        result = await github_service.analyze_github_profile(username)
        
        assert "ai_analysis" in result
        assert "overall_score" in result["ai_analysis"]
        assert isinstance(result["ai_analysis"]["overall_score"], int)

    @pytest.mark.asyncio
    async def test_analyze_github_profile_repos_with_description_count(self, mocker):
        """Test counting repos with and without descriptions."""
        username = "testuser"
        
        mock_github_data = {
            "user": {"name": "Test", "public_repos": 4},
            "repos": [
                {"description": "Has description", "language": "Python", "stargazers_count": 1},
                {"description": None, "language": "Python", "stargazers_count": 1},
                {"description": "Another description", "language": "Python", "stargazers_count": 1},
                {"description": "", "language": "Python", "stargazers_count": 1}
            ]
        }
        
        mock_fetch = mocker.patch('app.services.github_service.fetch_github_data', new_callable=AsyncMock)
        mock_fetch.return_value = mock_github_data
        
        mock_groq = mocker.patch('app.services.github_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(github_service._mock_github_analysis()).replace("'", '"')
        
        import json
        with mocker.patch('json.loads', return_value=github_service._mock_github_analysis()):
            result = await github_service.analyze_github_profile(username)
        
        # Should count repos with truthy descriptions
        assert result["repos_with_description"] == 2
        assert result["repos_without_description"] == 2


@pytest.mark.unit
class TestGitHubMockAnalysis:
    """Test mock GitHub analysis fallback."""

    def test_mock_github_analysis_structure(self):
        """Test that mock analysis has correct structure."""
        result = github_service._mock_github_analysis()
        
        assert "overall_score" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert "suggestions" in result
        assert "missing_aspects" in result
        assert "profile_grade" in result
        assert "career_readiness" in result
        assert "summary" in result
        
        # Verify types
        assert isinstance(result["overall_score"], int)
        assert isinstance(result["strengths"], list)
        assert isinstance(result["suggestions"], list)
        
        # Verify suggestions structure
        if result["suggestions"]:
            suggestion = result["suggestions"][0]
            assert "priority" in suggestion
            assert "suggestion" in suggestion
            assert "reason" in suggestion
            assert suggestion["priority"] in ["high", "medium", "low"]
