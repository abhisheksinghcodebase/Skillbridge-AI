# Implementation Plan: Backend Missing Implementations

## Overview

This implementation plan addresses critical missing components in the SkillBridge AI backend: Alembic database migration infrastructure, comprehensive pytest-based test suite with mocking, Google OAuth 2.0 integration, and an optional projects module with full CRUD API. The approach prioritizes test infrastructure first, followed by database migrations, OAuth integration, and finally the optional projects feature.

## Tasks

- [x] 1. Set up Alembic migration infrastructure
  - [x] 1.1 Initialize Alembic and create configuration files
    - Run `alembic init alembic` to create directory structure
    - Create `alembic.ini` with async PostgreSQL configuration
    - Create `alembic/env.py` with async engine setup, importing all models (User, Resume, ChatMessage, Roadmap, GitHubAnalysis, LearningProgress, InterviewSession)
    - Configure `env.py` to use `settings.DATABASE_URL` from app configuration
    - Implement both `run_migrations_offline()` and `run_migrations_online()` functions
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 1.2 Generate initial database migration
    - Run `alembic revision --autogenerate -m "Initial schema with all existing tables"`
    - Verify migration file creates: users, resumes, chat_messages, roadmaps, github_analyses, learning_progress, interview_sessions tables
    - Verify all foreign keys, indexes, and constraints are captured
    - Test migration with `alembic upgrade head` on clean database
    - Test rollback with `alembic downgrade base`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_

- [x] 2. Create test infrastructure and fixtures
  - [x] 2.1 Set up pytest configuration and test database
    - Install test dependencies: pytest, pytest-asyncio, pytest-cov, pytest-mock, aiosqlite, httpx
    - Create `tests/conftest.py` with async test database fixture using in-memory SQLite
    - Implement `async_test_db` fixture creating tables and providing AsyncSession
    - Implement `client` fixture providing TestClient with dependency overrides
    - Configure pytest.ini with asyncio settings and coverage options
    - _Requirements: 5.8, 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x] 2.2 Create reusable test fixtures
    - Implement `test_user` fixture creating sample user with password authentication
    - Implement `test_oauth_user` fixture creating sample user with Google OAuth
    - Implement `test_resume` fixture creating sample resume linked to test_user
    - Implement `test_chat_messages` fixture creating sample chat history
    - Implement `auth_token` fixture generating valid JWT token for test_user
    - Implement `auth_headers` fixture providing authorization headers
    - _Requirements: 5.1, 5.2, 5.3, 13.5_

- [ ] 3. Implement unit tests for service layer
  - [x] 3.1 Create unit tests for resume service
    - Test `parse_resume()` with valid PDF inputs
    - Test `analyze_resume()` scoring calculation (ATS score and overall score)
    - Mock Groq API responses for resume analysis
    - Test error handling for invalid file formats
    - _Requirements: 3.1, 3.2, 3.7, 3.8, 9.2_
  
  - [x] 3.2 Create unit tests for roadmap service
    - Test `generate_roadmap()` with various career goals
    - Mock Groq API responses for roadmap generation
    - Test roadmap structure validation
    - _Requirements: 3.3, 3.7, 9.4_
  
  - [x] 3.3 Create unit tests for GitHub service
    - Test `analyze_github_profile()` with mock GitHub API responses
    - Test repository analysis and commit history parsing
    - Mock httpx responses for GitHub API endpoints
    - Test error handling for invalid usernames
    - _Requirements: 3.4, 3.7, 3.8, 9.5, 9.6, 9.7, 9.8_
  
  - [x] 3.4 Create unit tests for RAG service
    - Test document retrieval from ChromaDB
    - Test query embedding and similarity search
    - Mock ChromaDB collection responses
    - _Requirements: 3.6, 3.7_
  
  - [ ] 3.5 Generate coverage report for service layer
    - Run `pytest tests/unit/ --cov=app/services --cov-report=html`
    - Verify at least 80% coverage for service layer
    - _Requirements: 3.9, 10.1, 10.2, 10.3, 10.4_

- [ ] 4. Checkpoint - Review test infrastructure
  - Ensure all tests pass, verify test isolation works correctly, ask the user if questions arise.

- [ ] 5. Implement integration tests for existing API endpoints
  - [ ] 5.1 Create integration tests for auth endpoints
    - Test POST /auth/register with valid and invalid payloads
    - Test POST /auth/login with correct and incorrect credentials
    - Test 422 validation errors for missing required fields
    - _Requirements: 4.1, 4.2, 4.14, 4.15, 13.1, 13.2, 13.3, 13.4_
  
  - [ ] 5.2 Create integration tests for resume endpoints
    - Test POST /resume/upload with authenticated user
    - Test GET /resume/analysis/{resume_id} with authorization checks
    - Test 401 response when accessing without authentication
    - Test 403 response when accessing another user's resume
    - Mock Groq API for resume analysis
    - _Requirements: 4.3, 4.4, 4.14, 9.2_
  
  - [ ] 5.3 Create integration tests for chat endpoints
    - Test POST /chat/message with valid session_id
    - Test GET /chat/history with pagination
    - Mock Groq API for chat completions
    - _Requirements: 4.5, 4.6, 9.1_
  
  - [ ] 5.4 Create integration tests for roadmap endpoints
    - Test POST /roadmap/generate with various career goals
    - Test GET /roadmap with user-specific filtering
    - Mock Groq API for roadmap generation
    - _Requirements: 4.7, 4.8, 9.4_
  
  - [ ] 5.5 Create integration tests for GitHub and interview endpoints
    - Test POST /github/analyze with valid GitHub usernames
    - Test POST /interview/start with topic specification
    - Test POST /interview/submit-answer with feedback generation
    - Mock GitHub API and Groq API responses
    - _Requirements: 4.9, 4.10, 4.11, 9.5, 9.6, 9.7, 9.8, 9.4_
  
  - [ ] 5.6 Create integration tests for tracker and jobs endpoints
    - Test POST /tracker/update with progress tracking
    - Test GET /jobs/search with query parameters
    - _Requirements: 4.12, 4.13_

- [ ] 6. Implement database-specific tests
  - [ ] 6.1 Create database constraint tests
    - Test unique email constraint enforcement
    - Test foreign key cascade deletes (user deletion cascades to resumes, chat messages)
    - Test NOT NULL constraints on required fields
    - _Requirements: 5.4_
  
  - [ ] 6.2 Create database transaction tests
    - Test transaction rollback on error
    - Test atomic operations for multi-step database changes
    - _Requirements: 5.5_
  
  - [ ] 6.3 Create database concurrency tests
    - Test concurrent read operations with multiple sessions
    - Test concurrent write operations to different records
    - _Requirements: 5.6_

- [ ] 7. Checkpoint - Review test suite completeness
  - Ensure all tests pass, review coverage report, ask the user if questions arise.

- [ ] 8. Implement Google OAuth integration
  - [ ] 8.1 Add OAuth configuration and database schema changes
    - Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` to `app/core/config.py`
    - Generate Alembic migration: `alembic revision --autogenerate -m "Add OAuth fields to users table"`
    - Verify migration adds `oauth_provider`, `oauth_id` columns and makes `hashed_password` nullable
    - Apply migration with `alembic upgrade head`
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ] 8.2 Implement OAuth service functions
    - Create `app/services/oauth_service.py` with `create_oauth_user()` function
    - Implement user creation or linking logic for OAuth users
    - Handle case where email already exists with password authentication
    - _Requirements: 6.6, 6.7_
  
  - [ ] 8.3 Implement OAuth endpoints in auth router
    - Implement GET /auth/google/login endpoint generating OAuth redirect URL
    - Implement GET /auth/google/callback endpoint handling code exchange
    - Implement state parameter generation and validation for CSRF protection
    - Exchange authorization code for Google access token using authlib
    - Fetch user profile (email, name, picture) from Google API
    - Create or update user in database using OAuth service
    - Generate JWT access token identical to password authentication flow
    - _Requirements: 6.4, 6.5, 6.6, 6.8, 6.9, 6.10_
  
  - [ ] 8.4 Create integration tests for OAuth endpoints
    - Test GET /auth/google/login returns valid redirect URL with state parameter
    - Test GET /auth/google/callback with valid authorization code
    - Test state validation (CSRF protection)
    - Test user creation for new Google users
    - Test account linking for existing email addresses
    - Mock Google OAuth API responses
    - _Requirements: 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10_

- [ ] 9. Implement optional projects module
  - [ ] 9.1 Create Project model and migration
    - Create `app/models/project.py` with Project model (id, user_id, title, description, tech_stack, github_url, live_url, thumbnail_url, timestamps)
    - Import Project model in `alembic/env.py`
    - Generate migration: `alembic revision --autogenerate -m "Create projects table"`
    - Verify migration includes CASCADE delete foreign key, user_id index
    - Apply migration with `alembic upgrade head`
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ] 9.2 Create Project Pydantic schemas
    - Create `app/schemas/project.py` with ProjectBase, ProjectCreate, ProjectUpdate, ProjectOut schemas
    - Implement validation for required fields (title, description)
    - Implement validation for tech_stack as list[str]
    - _Requirements: 8.8, 8.9_
  
  - [ ] 9.3 Implement Projects API endpoints
    - Create `app/api/routers/projects.py` router
    - Implement POST /projects creating project for authenticated user
    - Implement GET /projects listing user's projects
    - Implement GET /projects/{project_id} retrieving specific project
    - Implement PUT /projects/{project_id} updating project with ownership check
    - Implement DELETE /projects/{project_id} deleting project with ownership check
    - Register router in `app/main.py`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_
  
  - [ ] 9.4 Create integration tests for Projects API
    - Test POST /projects with valid and invalid payloads
    - Test GET /projects returns only authenticated user's projects
    - Test GET /projects/{id} with ownership validation
    - Test PUT /projects/{id} with ownership check (403 for non-owner)
    - Test DELETE /projects/{id} with ownership check
    - Test 401 responses for unauthenticated requests
    - Test 404 responses for non-existent projects
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9_
  
  - [ ] 9.5 Create database tests for Project model
    - Test CASCADE delete when user is deleted
    - Test user_id foreign key constraint
    - Test tech_stack JSON serialization/deserialization
    - _Requirements: 7.1, 7.3_

- [ ] 10. Create test documentation and performance tests
  - [ ] 10.1 Create test documentation
    - Create `tests/README.md` documenting test execution commands
    - Document test organization structure (unit, integration, database)
    - Document fixture usage and how to write new tests
    - Document commands for running specific test categories
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ] 10.2 Create performance tests for critical endpoints
    - Test resume upload and analysis completes within 10 seconds for 5MB files
    - Test chat message retrieval completes within 500ms for 100 messages
    - Test roadmap generation completes within 15 seconds
    - Test GitHub analysis completes within 20 seconds for 50 repositories
    - Test concurrent request handling (10+ simultaneous requests)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 11. Final checkpoint and migration documentation
  - [ ] 11.1 Create migration documentation
    - Document Alembic commands in `backend/README.md` or `alembic/README.md`
    - Document migration generation workflow
    - Document how to apply and rollback migrations
    - Document database URL configuration
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_
  
  - [ ] 11.2 Final validation and cleanup
    - Run full test suite with coverage: `pytest --cov=app --cov-report=html`
    - Verify all migrations apply cleanly: `alembic upgrade head`
    - Verify all migrations rollback cleanly: `alembic downgrade base`
    - Ensure all tests pass, review final coverage report, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Test infrastructure (tasks 2-7) should be completed before OAuth and Projects features
- Alembic migrations should be tested with both upgrade and downgrade to ensure reversibility
- All external API dependencies (Groq, GitHub) must be mocked in tests for reliability
- Test database uses SQLite in-memory for isolation; production uses PostgreSQL
- OAuth implementation is backward-compatible with existing password authentication
- Projects module is entirely optional and can be implemented independently
- Each test category (unit, integration, database) can be run independently
- Coverage target is 80% for service layer and overall codebase
- Checkpoint tasks ensure incremental validation and user involvement

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["3.1", "3.2", "3.3", "3.4"] },
    { "id": 4, "tasks": ["3.5", "5.1", "5.2", "5.3"] },
    { "id": 5, "tasks": ["5.4", "5.5", "5.6", "6.1"] },
    { "id": 6, "tasks": ["6.2", "6.3"] },
    { "id": 7, "tasks": ["8.1"] },
    { "id": 8, "tasks": ["8.2"] },
    { "id": 9, "tasks": ["8.3"] },
    { "id": 10, "tasks": ["8.4", "9.1"] },
    { "id": 11, "tasks": ["9.2"] },
    { "id": 12, "tasks": ["9.3"] },
    { "id": 13, "tasks": ["9.4", "9.5", "10.1"] },
    { "id": 14, "tasks": ["10.2", "11.1"] },
    { "id": 15, "tasks": ["11.2"] }
  ]
}
```
