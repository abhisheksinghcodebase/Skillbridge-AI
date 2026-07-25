import pytest
from httpx import AsyncClient
from app.services.groq_service import groq_service
from app.services.resume_service import analyze_resume
from app.services.github_service import _mock_github_analysis
from app.services.portfolio_service import _mock_portfolio_audit


@pytest.mark.asyncio
async def test_groq_service_mock_fallback():
    response = await groq_service.chat_completion(
        messages=[{"role": "user", "content": "Hello AI Mentor"}]
    )
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_resume_service_analysis():
    sample_text = "Python Developer with experience in FastAPI, PostgreSQL, Docker, and React."
    result = await analyze_resume(sample_text)
    assert "resume_score" in result
    assert "ats_score" in result
    assert "strong_skills" in result
    assert isinstance(result["strong_skills"], list)


def test_mock_github_analysis():
    data = _mock_github_analysis()
    assert "overall_score" in data
    assert "strengths" in data
    assert data["profile_grade"] in ["A", "B", "C", "D"]


def test_mock_portfolio_audit():
    audit = _mock_portfolio_audit("https://example.dev")
    assert audit["portfolio_url"] == "https://example.dev"
    assert "ui_ux_score" in audit
    assert "seo_score" in audit


@pytest.mark.asyncio
async def test_authenticated_feature_endpoints(client: AsyncClient):
    # Register test user
    reg = await client.post(
        "/auth/register",
        json={"name": "Feature User", "email": "featuser@example.com", "password": "Password123!"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test Project Recommendations
    proj_resp = await client.post(
        "/projects/recommend",
        json={"skills": ["Python", "FastAPI"], "goal": "Backend Developer"},
        headers=headers,
    )
    assert proj_resp.status_code == 200
    assert "projects" in proj_resp.json()

    # Test Cover Letter Tool
    cover_resp = await client.post(
        "/phase3/tools/cover-letter",
        json={"target_role": "Junior SDE", "company_name": "Tech Corp"},
        headers=headers,
    )
    assert cover_resp.status_code == 200
    assert "cover_letter" in cover_resp.json()
