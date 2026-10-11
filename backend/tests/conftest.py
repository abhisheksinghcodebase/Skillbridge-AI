"""
Pytest configuration and shared fixtures for SkillBridge AI backend tests using MongoDB mock.
"""
import uuid
from datetime import datetime
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import mongomock_motor

from app.main import app
from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.resume import Resume
from app.models.chat import ChatMessage

# Create in-memory mock MongoDB client
mock_client = mongomock_motor.AsyncMongoMockClient()
mock_db = mock_client["test_skillbridge_db"]


async def override_get_db():
    return mock_db


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def clean_database():
    """Clean all collections before each test."""
    collections = await mock_db.list_collection_names()
    for col in collections:
        await mock_db[col].delete_many({})
    yield
    collections = await mock_db.list_collection_names()
    for col in collections:
        await mock_db[col].delete_many({})


@pytest_asyncio.fixture
async def async_test_db():
    return mock_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver/api/v1") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(async_test_db) -> User:
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        college="Test College",
        branch="Computer Science",
        year="3rd Year",
        skills=["Python", "FastAPI", "React"],
        is_active=True,
    )
    await async_test_db.users.insert_one(user.to_doc())
    return user


@pytest_asyncio.fixture
async def test_oauth_user(async_test_db) -> User:
    user = User(
        name="OAuth User",
        email="oauth@example.com",
        hashed_password="",
        college="OAuth College",
        branch="Software Engineering",
        year="4th Year",
        skills=["JavaScript", "TypeScript", "Node.js"],
        is_active=True,
    )
    await async_test_db.users.insert_one(user.to_doc())
    return user


@pytest_asyncio.fixture
async def test_resume(async_test_db, test_user: User) -> Resume:
    resume = Resume(
        user_id=test_user.id,
        filename="test_resume.pdf",
        file_path="/uploads/test_resume.pdf",
        raw_text="Sample resume text with Python and FastAPI experience...",
        resume_score=85.0,
        ats_score=90.0,
        strong_skills=["Python", "FastAPI", "REST APIs"],
        weak_skills=["Machine Learning", "Docker"],
        grammar_issues=["Minor typo"],
        formatting_suggestions=["Add more whitespace", "Use bullet points"],
        missing_keywords=["Kubernetes", "CI/CD"],
        improvement_tips=["Add measurable achievements", "Quantify impact"],
        experience_years=2.5,
        education={"degree": "B.Tech", "institution": "Test College"},
        projects_detected=["Project A", "Project B"],
        full_analysis={"summary": "Strong technical background"},
    )
    await async_test_db.resumes.insert_one(resume.to_doc())
    return resume


@pytest_asyncio.fixture
async def test_chat_messages(async_test_db, test_user: User) -> list[ChatMessage]:
    session_id = str(uuid.uuid4())
    messages = [
        ChatMessage(
            user_id=test_user.id,
            role="user",
            content="Hello, I need help with my resume",
            session_id=session_id,
        ),
        ChatMessage(
            user_id=test_user.id,
            role="assistant",
            content="I'd be happy to help! Please upload your resume.",
            session_id=session_id,
        ),
        ChatMessage(
            user_id=test_user.id,
            role="user",
            content="How can I improve my Python skills section?",
            session_id=session_id,
        ),
    ]
    for msg in messages:
        await async_test_db.chat_messages.insert_one(msg.to_doc())
    return messages


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    token_data = {
        "sub": str(test_user.id),
        "email": test_user.email,
    }
    return create_access_token(data=token_data)


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}
