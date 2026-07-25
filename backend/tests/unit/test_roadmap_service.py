"""
Unit tests for roadmap service.

Tests:
- Roadmap generation with various career goals
- Mock Groq API responses
- Roadmap structure validation
"""
import pytest
from unittest.mock import AsyncMock
from app.services import roadmap_service


@pytest.mark.unit
class TestRoadmapGeneration:
    """Test roadmap generation functionality."""

    @pytest.mark.asyncio
    async def test_generate_roadmap_with_valid_goal(self, mocker):
        """Test generating roadmap for a valid career goal."""
        goal = "Become a Full Stack Developer"
        
        mock_roadmap = {
            "goal": goal,
            "estimated_months": 8,
            "phases": [
                {
                    "phase": 1,
                    "title": "Frontend Basics",
                    "duration_weeks": 4,
                    "nodes": [
                        {
                            "id": "node-1",
                            "title": "HTML & CSS",
                            "description": "Learn web structure and styling",
                            "resources": ["MDN Web Docs", "freeCodeCamp"],
                            "difficulty": "beginner",
                            "estimated_hours": 30,
                            "prerequisites": [],
                            "skills_gained": ["HTML", "CSS"]
                        }
                    ]
                }
            ],
            "final_projects": ["Build a portfolio website", "Create a full-stack app"],
            "job_titles": ["Full Stack Developer", "Web Developer"],
            "tips": ["Practice daily", "Build projects"]
        }
        
        mock_groq = mocker.patch('app.services.roadmap_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(mock_roadmap).replace("'", '"')
        
        import json
        with mocker.patch('json.loads', return_value=mock_roadmap):
            result = await roadmap_service.generate_roadmap(goal)
        
        assert result["goal"] == goal
        assert result["estimated_months"] == 8
        assert len(result["phases"]) == 1
        assert result["phases"][0]["title"] == "Frontend Basics"
        mock_groq.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_roadmap_with_current_skills(self, mocker):
        """Test roadmap generation considers current skills."""
        goal = "Become a Data Scientist"
        current_skills = ["Python", "Statistics"]
        
        mock_roadmap = {
            "goal": goal,
            "estimated_months": 6,
            "phases": [
                {
                    "phase": 1,
                    "title": "Machine Learning",
                    "duration_weeks": 6,
                    "nodes": []
                }
            ],
            "final_projects": ["ML project"],
            "job_titles": ["Data Scientist"],
            "tips": ["Keep learning"]
        }
        
        mock_groq = mocker.patch('app.services.roadmap_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(mock_roadmap).replace("'", '"')
        
        import json
        with mocker.patch('json.loads', return_value=mock_roadmap):
            result = await roadmap_service.generate_roadmap(goal, current_skills)
        
        # Verify that current_skills were passed in the prompt
        call_args = mock_groq.call_args
        messages = call_args[1]["messages"]
        user_message = messages[1]["content"]
        
        assert "Python" in user_message
        assert "Statistics" in user_message
        assert result["goal"] == goal

    @pytest.mark.asyncio
    async def test_generate_roadmap_handles_groq_api_error(self, mocker):
        """Test error handling when Groq API fails."""
        goal = "Become a DevOps Engineer"
        
        mock_groq = mocker.patch('app.services.roadmap_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.side_effect = Exception("Groq API error")
        
        result = await roadmap_service.generate_roadmap(goal)
        
        # Should return mock roadmap on error
        assert result["goal"] == goal
        assert "phases" in result
        assert "estimated_months" in result
        assert isinstance(result["phases"], list)

    @pytest.mark.asyncio
    async def test_generate_roadmap_handles_invalid_json(self, mocker):
        """Test handling of invalid JSON response from Groq."""
        goal = "Learn Mobile Development"
        
        mock_groq = mocker.patch('app.services.roadmap_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = "Invalid JSON {{"
        
        result = await roadmap_service.generate_roadmap(goal)
        
        # Should return mock roadmap on JSON decode error
        assert result["goal"] == goal
        assert "phases" in result


@pytest.mark.unit
class TestRoadmapStructureValidation:
    """Test roadmap data structure validation."""

    @pytest.mark.asyncio
    async def test_mock_roadmap_structure(self):
        """Test that mock roadmap has correct structure."""
        goal = "Test Goal"
        result = roadmap_service._mock_roadmap(goal)
        
        # Verify required top-level fields
        assert "goal" in result
        assert "estimated_months" in result
        assert "phases" in result
        assert "final_projects" in result
        assert "job_titles" in result
        assert "tips" in result
        
        # Verify phases structure
        assert isinstance(result["phases"], list)
        assert len(result["phases"]) > 0
        
        # Verify each phase has required fields
        for phase in result["phases"]:
            assert "phase" in phase
            assert "title" in phase
            assert "duration_weeks" in phase
            assert "nodes" in phase
            assert isinstance(phase["nodes"], list)
        
        # Verify node structure
        if result["phases"][0]["nodes"]:
            node = result["phases"][0]["nodes"][0]
            assert "id" in node
            assert "title" in node
            assert "description" in node
            assert "resources" in node
            assert "difficulty" in node
            assert "estimated_hours" in node
            assert "prerequisites" in node
            assert "skills_gained" in node

    @pytest.mark.asyncio
    async def test_roadmap_phases_are_sequential(self):
        """Test that roadmap phases are properly numbered."""
        goal = "Test Goal"
        result = roadmap_service._mock_roadmap(goal)
        
        for i, phase in enumerate(result["phases"], start=1):
            assert phase["phase"] == i

    @pytest.mark.asyncio
    async def test_roadmap_nodes_have_unique_ids(self):
        """Test that all nodes in roadmap have unique IDs."""
        goal = "Test Goal"
        result = roadmap_service._mock_roadmap(goal)
        
        node_ids = set()
        for phase in result["phases"]:
            for node in phase["nodes"]:
                assert node["id"] not in node_ids, f"Duplicate node ID: {node['id']}"
                node_ids.add(node["id"])

    @pytest.mark.asyncio
    async def test_roadmap_difficulty_levels(self):
        """Test that difficulty levels are valid."""
        goal = "Test Goal"
        result = roadmap_service._mock_roadmap(goal)
        
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        
        for phase in result["phases"]:
            for node in phase["nodes"]:
                assert node["difficulty"] in valid_difficulties

    @pytest.mark.asyncio
    async def test_generate_roadmap_without_skills(self, mocker):
        """Test roadmap generation when no current skills provided."""
        goal = "Learn Web Development"
        
        mock_roadmap = {
            "goal": goal,
            "estimated_months": 6,
            "phases": [],
            "final_projects": [],
            "job_titles": [],
            "tips": []
        }
        
        mock_groq = mocker.patch('app.services.roadmap_service.groq_service.chat_completion', new_callable=AsyncMock)
        mock_groq.return_value = str(mock_roadmap).replace("'", '"')
        
        import json
        with mocker.patch('json.loads', return_value=mock_roadmap):
            result = await roadmap_service.generate_roadmap(goal, None)
        
        # Should handle None skills gracefully
        call_args = mock_groq.call_args
        messages = call_args[1]["messages"]
        user_message = messages[1]["content"]
        
        assert "None mentioned" in user_message or "current_skills" in user_message
