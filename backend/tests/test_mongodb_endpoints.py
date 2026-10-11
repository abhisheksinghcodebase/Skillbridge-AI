"""
Integration tests verifying all MongoDB CRUD operations across API endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_mongodb(client: AsyncClient):
    response = await client.get("http://testserver/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "mongodb"


@pytest.mark.asyncio
async def test_user_profile_crud_mongodb(client: AsyncClient):
    # Register
    reg_resp = await client.post(
        "/auth/register",
        json={
            "name": "Mongo User",
            "email": "mongouser@example.com",
            "password": "Password123!",
            "college": "Tech Institute",
            "branch": "IT",
            "year": "4th Year",
            "skills": ["Python", "MongoDB"],
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get Me
    me_resp = await client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "mongouser@example.com"
    assert me_resp.json()["skills"] == ["Python", "MongoDB"]

    # Update Me
    up_resp = await client.put(
        "/auth/me",
        json={"college": "New University", "skills": ["Python", "FastAPI", "MongoDB"]},
        headers=headers,
    )
    assert up_resp.status_code == 200
    assert up_resp.json()["college"] == "New University"
    assert "FastAPI" in up_resp.json()["skills"]


@pytest.mark.asyncio
async def test_roadmap_endpoints_mongodb(client: AsyncClient, auth_headers: dict):
    # Create roadmap
    gen_resp = await client.post(
        "/roadmap/generate",
        json={"goal": "AI Engineer", "current_skills": ["Python"]},
        headers=auth_headers,
    )
    assert gen_resp.status_code == 201
    roadmap_data = gen_resp.json()
    assert roadmap_data["goal"] == "AI Engineer"
    roadmap_id = roadmap_data["id"]

    # List roadmaps
    list_resp = await client.get("/roadmap/", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Update progress
    prog_resp = await client.put(
        f"/roadmap/{roadmap_id}/progress",
        json={"node_id": "step_1", "completed": True},
        headers=auth_headers,
    )
    assert prog_resp.status_code == 200
    assert prog_resp.json()["progress"]["step_1"] is True


@pytest.mark.asyncio
async def test_tracker_endpoints_mongodb(client: AsyncClient, auth_headers: dict):
    # Add skill
    add_resp = await client.post(
        "/tracker/",
        json={
            "skill_name": "MongoDB",
            "category": "Database",
            "progress_percent": 80,
            "status": "in_progress",
            "notes": "Learning aggregation pipelines",
        },
        headers=auth_headers,
    )
    assert add_resp.status_code == 201
    skill_data = add_resp.json()
    assert skill_data["skill_name"] == "MongoDB"
    skill_id = skill_data["id"]

    # Get tracker list
    list_resp = await client.get("/tracker/", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Update skill
    up_resp = await client.put(
        f"/tracker/{skill_id}",
        json={
            "skill_name": "MongoDB",
            "category": "Database",
            "progress_percent": 100,
            "status": "completed",
            "notes": "Mastered indexing and aggregation",
        },
        headers=auth_headers,
    )
    assert up_resp.status_code == 200
    assert up_resp.json()["progress_percent"] == 100
    assert up_resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_chat_history_mongodb(client: AsyncClient, auth_headers: dict, test_chat_messages):
    resp = await client.get("/chat/history", headers=auth_headers)
    assert resp.status_code == 200
    messages = resp.json()
    assert len(messages) == 3


@pytest.mark.asyncio
async def test_resume_endpoints_mongodb(client: AsyncClient, auth_headers: dict, test_resume):
    # Get latest
    latest_resp = await client.get("/resume/latest", headers=auth_headers)
    assert latest_resp.status_code == 200
    assert latest_resp.json()["filename"] == "test_resume.pdf"
    assert latest_resp.json()["resume_score"] == 85.0

    # Get history
    hist_resp = await client.get("/resume/history", headers=auth_headers)
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
