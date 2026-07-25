"""
Pytest configuration and shared fixtures for SkillBridge AI backend tests.

This module provides:
- async_test_db: In-memory SQLite database fixture with fresh schema per test
- client: TestClient with dependency overrides for API integration tests
- Event loop configuration for async tests
- Reusable test fixtures: test_user, test_oauth_user, test_resume, test_chat_messages
- Authentication fixtures: auth_token, auth_headers
"""
import asyncio
import uuid
from datetime import datetime, timedelta
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.resume import Resume
from app.models.chat import ChatMessage

# Use in-memory SQLite for fast testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine with StaticPool for in-memory database
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_test_db() -> AsyncSession:
    """
    Provide an async test database session with fresh schema.
    
    This fixture:
    - Creates all tables from SQLAlchemy models
    - Provides an AsyncSession for database operations
    - Automatically cleans up after each test
    
    Usage:
        async def test_create_user(async_test_db):
            user = User(name="Test", email="test@example.com")
            async_test_db.add(user)
            await async_test_db.commit()
    """
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Provide session
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # Drop all tables for cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    """Override the get_db dependency for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    """
    Provide a test client with dependency overrides.
    
    This fixture:
    - Uses the test database via dependency override
    - Provides an AsyncClient for making HTTP requests
    - Base URL set to http://testserver/api/v1
    
    Usage:
        async def test_register(client):
            response = await client.post("/auth/register", json={...})
            assert response.status_code == 201
    """
    # Ensure tables exist before client operations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver/api/v1") as ac:
        yield ac
    
    # Cleanup after client tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ==================== Reusable Test Data Fixtures ====================

@pytest_asyncio.fixture
async def test_user(async_test_db: AsyncSession) -> User:
    """
    Create a test user with password authentication.
    
    Returns:
        User with email: test@example.com, password: testpassword123
    
    Usage:
        async def test_something(test_user):
            assert test_user.email == "test@example.com"
    """
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        college="Test College",
        branch="Computer Science",
        year="3rd Year",
        skills=["Python", "FastAPI", "React"],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_test_db.add(user)
    await async_test_db.commit()
    await async_test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_oauth_user(async_test_db: AsyncSession) -> User:
    """
    Create a test user with Google OAuth authentication.
    
    Returns:
        User with OAuth provider, no password
    
    Usage:
        async def test_oauth_flow(test_oauth_user):
            assert test_oauth_user.oauth_provider == "google"
    """
    user = User(
        id=uuid.uuid4(),
        name="OAuth User",
        email="oauth@example.com",
        hashed_password=None,  # OAuth users don't have password
        college="OAuth College",
        branch="Software Engineering",
        year="4th Year",
        skills=["JavaScript", "TypeScript", "Node.js"],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_test_db.add(user)
    await async_test_db.commit()
    await async_test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_resume(async_test_db: AsyncSession, test_user: User) -> Resume:
    """
    Create a test resume linked to test_user.
    
    Args:
        async_test_db: Test database session
        test_user: User fixture
    
    Returns:
        Resume with sample analysis data
    
    Usage:
        async def test_resume_analysis(test_resume):
            assert test_resume.resume_score == 85.0
    """
    resume = Resume(
        id=uuid.uuid4(),
        user_id=test_user.id,
        filename="test_resume.pdf",
        file_path="/uploads/test_resume.pdf",
        raw_text="Sample resume text with Python and FastAPI experience...",
        resume_score=85.0,
        ats_score=90.0,
        strong_skills=["Python", "FastAPI", "REST APIs"],
        weak_skills=["Machine Learning", "Docker"],
        grammar_issues=[{"issue": "Minor typo", "line": 5}],
        formatting_suggestions=["Add more whitespace", "Use bullet points"],
        missing_keywords=["Kubernetes", "CI/CD"],
        improvement_tips=["Add measurable achievements", "Quantify impact"],
        experience_years=2.5,
        education=[{"degree": "B.Tech", "institution": "Test College"}],
        projects_detected=["Project A", "Project B"],
        full_analysis={"summary": "Strong technical background"},
        created_at=datetime.utcnow(),
    )
    async_test_db.add(resume)
    await async_test_db.commit()
    await async_test_db.refresh(resume)
    return resume


@pytest_asyncio.fixture
async def test_chat_messages(async_test_db: AsyncSession, test_user: User) -> list[ChatMessage]:
    """
    Create sample chat messages for test_user.
    
    Args:
        async_test_db: Test database session
        test_user: User fixture
    
    Returns:
        List of 3 chat messages (user, assistant, user)
    
    Usage:
        async def test_chat_history(test_chat_messages):
            assert len(test_chat_messages) == 3
    """
    session_id = str(uuid.uuid4())
    messages = [
        ChatMessage(
            id=uuid.uuid4(),
            user_id=test_user.id,
            role="user",
            content="Hello, I need help with my resume",
            session_id=session_id,
            created_at=datetime.utcnow(),
        ),
        ChatMessage(
            id=uuid.uuid4(),
            user_id=test_user.id,
            role="assistant",
            content="I'd be happy to help! Please upload your resume.",
            session_id=session_id,
            created_at=datetime.utcnow(),
        ),
        ChatMessage(
            id=uuid.uuid4(),
            user_id=test_user.id,
            role="user",
            content="How can I improve my Python skills section?",
            session_id=session_id,
            created_at=datetime.utcnow(),
        ),
    ]
    for msg in messages:
        async_test_db.add(msg)
    await async_test_db.commit()
    for msg in messages:
        await async_test_db.refresh(msg)
    return messages


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """
    Generate a valid JWT token for test_user.
    
    Args:
        test_user: User fixture
    
    Returns:
        JWT access token string
    
    Usage:
        async def test_protected_endpoint(auth_token, client):
            response = await client.get("/protected", headers={"Authorization": f"Bearer {auth_token}"})
    """
    token_data = {
        "sub": str(test_user.id),
        "email": test_user.email,
    }
    access_token = create_access_token(data=token_data)
    return access_token


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict[str, str]:
    """
    Provide authorization headers with Bearer token.
    
    Args:
        auth_token: JWT token fixture
    
    Returns:
        Dict with Authorization header
    
    Usage:
        async def test_api(auth_headers, client):
            response = await client.get("/api/profile", headers=auth_headers)
    """
    return {"Authorization": f"Bearer {auth_token}"}
