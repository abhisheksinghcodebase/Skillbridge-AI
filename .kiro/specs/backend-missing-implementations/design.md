# Technical Design Document

## Overview

This document specifies the technical design for implementing critical missing components in the SkillBridge AI backend system. The implementation includes four major areas:

1. **Database Migration Infrastructure**: Alembic-based migration system with async PostgreSQL support
2. **Comprehensive Test Suite**: Pytest-based testing covering unit tests, integration tests, and database tests
3. **Google OAuth Integration**: OAuth 2.0 authentication flow alongside existing password authentication
4. **Optional Projects Module**: Database-backed project portfolio management with full CRUD API

### Key Design Principles

- **Async-First Architecture**: All database operations use SQLAlchemy async patterns with asyncpg
- **Test Isolation**: Tests use in-memory SQLite with function-scoped fixtures for complete isolation
- **Zero Breaking Changes**: All additions are backward-compatible with existing functionality
- **Mock-Based Testing**: External API dependencies (Groq, GitHub) are mocked for reliable testing

### Technology Stack

- **Database Migration**: Alembic 1.13.3 with async support
- **Testing Framework**: pytest 8.3.3 + pytest-asyncio 0.24.0
- **Test Database**: SQLite (aiosqlite 0.20.0) for in-memory testing
- **OAuth Library**: authlib 1.3.0 for Google OAuth 2.0
- **Coverage Tool**: pytest-cov for code coverage reporting
- **Mocking**: pytest-mock + httpx for external API mocking

## Architecture

### System Components

```mermaid
graph TD
    A[FastAPI Application] --> B[API Routers]
    A --> C[Database Layer]
    A --> D[Service Layer]
    
    B --> B1[Auth Router]
    B --> B2[Projects Router]
    B --> B3[Existing Routers]
    
    C --> C1[SQLAlchemy Models]
    C --> C2[Alembic Migrations]
    C --> C3[AsyncSession Pool]
    
    D --> D1[Resume Service]
    D --> D2[Groq Service]
    D --> D3[GitHub Service]
    D --> D4[RAG Service]
    
    E[Test Suite] --> E1[Unit Tests]
    E --> E2[Integration Tests]
    E --> E3[Database Tests]
    E1 --> F[Mock Objects]
    E2 --> G[Test Fixtures]
    E3 --> H[In-Memory SQLite]
    
    I[OAuth Flow] --> I1[Google OAuth Endpoint]
    I1 --> I2[Callback Handler]
    I2 --> C1
```

### Migration System Architecture

The Alembic migration system operates independently of the FastAPI application:

- **Configuration Layer**: `alembic.ini` with PostgreSQL connection settings
- **Environment Layer**: `env.py` with async engine configuration and model imports
- **Version Control**: Migration files in `alembic/versions/` with upgrade/downgrade functions
- **Execution**: CLI commands for generating, applying, and reverting migrations

### Test Suite Architecture

The test suite uses a three-tier approach:

1. **Unit Tests**: Test service functions in isolation with mocked external dependencies
2. **Integration Tests**: Test API endpoints end-to-end with test database
3. **Database Tests**: Test database constraints, transactions, and concurrency


**Test Isolation Strategy**:
- Each test runs against a fresh in-memory SQLite database
- Function-scoped fixtures ensure no data leakage between tests
- Database connections are closed after each test
- Parallel execution support via isolated database instances

### OAuth Architecture

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Google
    participant Database
    
    User->>Frontend: Click "Sign in with Google"
    Frontend->>Backend: GET /auth/google/login
    Backend->>Backend: Generate state token
    Backend->>Frontend: Redirect URL with state
    Frontend->>Google: Redirect to Google OAuth
    Google->>User: Request consent
    User->>Google: Grant permission
    Google->>Backend: GET /auth/google/callback?code=...&state=...
    Backend->>Backend: Validate state (CSRF protection)
    Backend->>Google: Exchange code for tokens
    Google->>Backend: Return access token + user info
    Backend->>Database: Create or update user
    Database->>Backend: User record
    Backend->>Backend: Generate JWT token
    Backend->>Frontend: Redirect with JWT token
    Frontend->>User: Authenticated session
```


## Components and Interfaces

### 1. Alembic Migration System

#### Configuration Files

**alembic.ini**
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname  # Placeholder, overridden in env.py

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```


**env.py** (Key Functions)
```python
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings
from app.core.database import Base

# Import all models to ensure they're registered with Base.metadata
from app.models.user import User
from app.models.resume import Resume
from app.models.chat import ChatMessage, Roadmap, GitHubAnalysis, LearningProgress, InterviewSession
from app.models.projects import Project  # New model

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' (SQL script generation) mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' (connected to database) mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
```


#### Migration Commands

| Command | Purpose |
|---------|---------|
| `alembic init alembic` | Initialize Alembic (one-time setup) |
| `alembic revision --autogenerate -m "message"` | Generate migration from model changes |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Rollback last migration |
| `alembic current` | Show current migration version |
| `alembic history` | Show migration history |

### 2. Database Schema Extensions

#### Modified User Model

```python
class User(Base):
    __tablename__ = "users"
    
    # Existing fields...
    id: Mapped[uuid.UUID]
    name: Mapped[str]
    email: Mapped[str]  # unique, indexed
    
    # Modified for OAuth support
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # New OAuth fields
    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "google"
    oauth_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    
    # Existing fields...
    college: Mapped[str | None]
    # ... rest of fields
```


#### New Project Model

```python
class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        index=True
    )
    
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    tech_stack: Mapped[list] = mapped_column(JSON)  # Array of technology strings
    
    github_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    live_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
```

**Database Constraints**:
- Primary key: `id` (UUID)
- Foreign key: `user_id` references `users.id` with CASCADE delete
- Index: `user_id` for efficient user-specific queries
- Unique constraint: `oauth_id` when not null (for User model)


### 3. Google OAuth Integration

#### Configuration Settings

```python
# app/core/config.py additions
class Settings(BaseSettings):
    # ... existing fields ...
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
```

#### OAuth Endpoints

**GET /auth/google/login**
- Generates a random state token for CSRF protection
- Stores state in memory cache with 10-minute expiration
- Constructs Google OAuth authorization URL with required scopes
- Returns redirect URL to frontend

**GET /auth/google/callback**
- Validates state parameter against stored state
- Exchanges authorization code for access token
- Fetches user profile from Google (email, name, picture)
- Creates new user or links existing user by email
- Generates JWT access token
- Returns token to frontend via redirect or JSON

#### OAuth Service Functions

```python
async def create_oauth_user(
    db: AsyncSession,
    email: str,
    name: str,
    oauth_provider: str,
    oauth_id: str,
    avatar_url: str | None = None
) -> User:
    """Create or update user from OAuth provider."""
```


### 4. Projects API

#### Pydantic Schemas

```python
class ProjectBase(BaseModel):
    title: str = Field(max_length=200)
    description: str
    tech_stack: list[str] = Field(default_factory=list)
    github_url: str | None = None
    live_url: str | None = None
    thumbnail_url: str | None = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    tech_stack: list[str] | None = None
    github_url: str | None = None
    live_url: str | None = None
    thumbnail_url: str | None = None

class ProjectOut(ProjectBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

#### API Endpoints

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/projects` | Create new project | Yes |
| GET | `/projects` | List user's projects | Yes |
| GET | `/projects/{id}` | Get specific project | Yes |
| PUT | `/projects/{id}` | Update project | Yes (owner only) |
| DELETE | `/projects/{id}` | Delete project | Yes (owner only) |


### 5. Test Infrastructure

#### Test Configuration (conftest.py enhancements)

```python
# Test fixtures to add

@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        college="Test College",
        branch="Computer Science",
        year="3rd Year"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Generate JWT token for test user."""
    return create_access_token({"sub": str(test_user.id)})

@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict:
    """Generate authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest_asyncio.fixture
async def test_resume(db: AsyncSession, test_user: User) -> Resume:
    """Create a test resume."""
    resume = Resume(
        user_id=test_user.id,
        filename="test_resume.pdf",
        file_path="/uploads/test_resume.pdf",
        resume_score=85.5,
        ats_score=78.0
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume
```


#### Test Organization Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_resume_service.py     # Resume parsing, analysis
│   ├── test_roadmap_service.py    # Roadmap generation
│   ├── test_github_service.py     # GitHub API interactions
│   ├── test_rag_service.py        # RAG document retrieval
│   └── test_security.py           # Token generation, password hashing
├── integration/
│   ├── __init__.py
│   ├── test_auth_api.py           # Auth endpoints
│   ├── test_resume_api.py         # Resume upload/analysis endpoints
│   ├── test_chat_api.py           # Chat endpoints
│   ├── test_roadmap_api.py        # Roadmap endpoints
│   ├── test_github_api.py         # GitHub analysis endpoints
│   ├── test_interview_api.py      # Interview endpoints
│   ├── test_tracker_api.py        # Progress tracking endpoints
│   └── test_projects_api.py       # Projects CRUD endpoints
└── database/
    ├── __init__.py
    ├── test_user_model.py         # User model constraints
    ├── test_resume_model.py       # Resume model relationships
    ├── test_chat_model.py         # Chat/roadmap models
    ├── test_project_model.py      # Project model
    ├── test_transactions.py       # Transaction rollback
    └── test_concurrency.py        # Concurrent access
```


#### Mock Strategy for External APIs

**Groq API Mocking**
```python
@pytest.fixture
def mock_groq_chat_completion(monkeypatch):
    """Mock Groq API chat completion."""
    async def mock_create(*args, **kwargs):
        return {
            "choices": [{
                "message": {
                    "content": "Mocked response content"
                }
            }]
        }
    monkeypatch.setattr("app.services.groq_service.groq_client.chat.completions.create", mock_create)
```

**GitHub API Mocking**
```python
@pytest.fixture
def mock_github_api(httpx_mock):
    """Mock GitHub API responses."""
    httpx_mock.add_response(
        url="https://api.github.com/users/testuser",
        json={
            "login": "testuser",
            "name": "Test User",
            "public_repos": 10,
            "followers": 50
        }
    )
    httpx_mock.add_response(
        url="https://api.github.com/users/testuser/repos",
        json=[
            {"name": "repo1", "language": "Python", "stargazers_count": 5},
            {"name": "repo2", "language": "JavaScript", "stargazers_count": 3}
        ]
    )
```


## Data Models

### Migration Schema Evolution

**Initial Migration (001_initial_schema.py)**
- Creates all existing tables: users, resumes, chat_messages, roadmaps, github_analyses, learning_progress, interview_sessions
- Establishes foreign key relationships
- Creates indexes on foreign keys and email

**OAuth Migration (002_add_oauth_fields.py)**
```python
def upgrade():
    op.add_column('users', sa.Column('oauth_provider', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(255), nullable=True))
    op.alter_column('users', 'hashed_password', nullable=True)
    op.create_unique_constraint('uq_users_oauth_id', 'users', ['oauth_id'])

def downgrade():
    op.drop_constraint('uq_users_oauth_id', 'users')
    op.alter_column('users', 'hashed_password', nullable=False)
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
```

**Projects Migration (003_create_projects_table.py)**
```python
def upgrade():
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('tech_stack', sa.JSON, nullable=False),
        sa.Column('github_url', sa.Text, nullable=True),
        sa.Column('live_url', sa.Text, nullable=True),
        sa.Column('thumbnail_url', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])
```

