# Requirements Document

## Introduction

This document specifies requirements for implementing missing critical components in the SkillBridge AI backend system. The SkillBridge AI platform is a FastAPI + PostgreSQL backend service providing AI-powered career mentoring features for students. Current gaps include database migration infrastructure, comprehensive test coverage, OAuth integration, and optional database schema enhancements.

## Glossary

- **Migration_System**: Alembic-based database migration management system
- **Test_Suite**: Pytest-based comprehensive testing infrastructure covering unit, integration, and database tests
- **OAuth_Module**: Google OAuth 2.0 authentication integration module
- **Project_Module**: Optional database-backed project portfolio management feature
- **Database_Schema**: SQLAlchemy models representing database tables
- **Service_Layer**: Business logic layer containing service functions (resume_service, groq_service, rag_service, roadmap_service, github_service, portfolio_service)
- **API_Endpoints**: FastAPI route handlers exposing REST API endpoints
- **Test_Database**: In-memory SQLite database used for test execution
- **Migration_File**: Alembic-generated Python file containing database schema changes
- **Test_Fixture**: Pytest fixture providing reusable test setup and teardown
- **Mock_Object**: Test double simulating external API behavior
- **ATS_Score**: Applicant Tracking System compatibility score for resumes
- **RAG_Service**: Retrieval-Augmented Generation service using ChromaDB
- **Groq_API**: External AI service provider API
- **GitHub_API**: External GitHub REST API for repository analysis

## Requirements

### Requirement 1: Initialize Alembic Migration System

**User Story:** As a developer, I want a properly configured Alembic migration system, so that I can manage database schema changes in a version-controlled and reproducible manner.

#### Acceptance Criteria

1. THE Migration_System SHALL create an alembic.ini configuration file with async PostgreSQL support
2. THE Migration_System SHALL create an env.py file with async engine configuration
3. WHEN the Migration_System is initialized, THE Migration_System SHALL support both online (connected) and offline (SQL script) migrations
4. THE Migration_System SHALL use the DATABASE_URL from the application settings
5. THE Migration_System SHALL import all SQLAlchemy models to ensure complete schema detection

### Requirement 2: Generate Initial Database Migration

**User Story:** As a developer, I want an initial migration capturing all existing models, so that I can establish a baseline database schema.

#### Acceptance Criteria

1. THE Migration_System SHALL generate a migration file creating the users table with all columns (id, name, email, hashed_password, college, branch, year, skills, resume_url, github_username, avatar_url, is_active, created_at, updated_at)
2. THE Migration_System SHALL generate a migration file creating the resumes table with all columns and foreign key to users
3. THE Migration_System SHALL generate a migration file creating the chat_messages table with user_id foreign key and session_id index
4. THE Migration_System SHALL generate a migration file creating the roadmaps table with user_id foreign key
5. THE Migration_System SHALL generate a migration file creating the github_analyses table with user_id foreign key
6. THE Migration_System SHALL generate a migration file creating the learning_progress table with user_id foreign key
7. THE Migration_System SHALL generate a migration file creating the interview_sessions table with user_id foreign key
8. WHEN a migration is applied, THE Migration_System SHALL create all tables with proper indexes, constraints, and foreign key relationships
9. WHEN a migration is rolled back, THE Migration_System SHALL drop all created tables in reverse dependency order

### Requirement 3: Create Comprehensive Unit Tests for Service Layer

**User Story:** As a developer, I want comprehensive unit tests for service functions, so that I can verify business logic correctness and catch regressions early.

#### Acceptance Criteria

1. THE Test_Suite SHALL test resume parsing functionality with valid PDF inputs
2. THE Test_Suite SHALL test resume analysis scoring calculation (ATS_Score and overall score)
3. THE Test_Suite SHALL test roadmap generation with various career goals
4. THE Test_Suite SHALL test GitHub repository analysis with mock GitHub_API responses
5. THE Test_Suite SHALL test portfolio generation logic
6. THE Test_Suite SHALL test RAG_Service document retrieval with ChromaDB
7. WHEN external APIs are unavailable, THE Test_Suite SHALL use Mock_Objects to isolate service logic
8. WHEN service functions receive invalid inputs, THE Test_Suite SHALL verify proper error handling
9. THE Test_Suite SHALL achieve at least 80% code coverage for the Service_Layer

### Requirement 4: Create Comprehensive Integration Tests for API Endpoints

**User Story:** As a developer, I want integration tests for all API endpoints, so that I can verify end-to-end request/response behavior.

#### Acceptance Criteria

1. THE Test_Suite SHALL test POST /auth/register with valid and invalid payloads
2. THE Test_Suite SHALL test POST /auth/login with correct and incorrect credentials
3. THE Test_Suite SHALL test POST /resume/upload with authenticated users
4. THE Test_Suite SHALL test GET /resume/analysis/{resume_id} with authorization checks
5. THE Test_Suite SHALL test POST /chat/message with valid session_id
6. THE Test_Suite SHALL test GET /chat/history with pagination
7. THE Test_Suite SHALL test POST /roadmap/generate with various career goals
8. THE Test_Suite SHALL test GET /roadmap with user-specific filtering
9. THE Test_Suite SHALL test POST /github/analyze with valid GitHub usernames
10. THE Test_Suite SHALL test POST /interview/start with topic specification
11. THE Test_Suite SHALL test POST /interview/submit-answer with feedback generation
12. THE Test_Suite SHALL test POST /tracker/update with progress tracking
13. THE Test_Suite SHALL test GET /jobs/search with query parameters
14. WHEN unauthorized requests are made, THE Test_Suite SHALL verify 401 responses
15. WHEN invalid data is submitted, THE Test_Suite SHALL verify 400/422 responses with descriptive error messages

### Requirement 5: Create Database Tests with Fixtures

**User Story:** As a developer, I want database-specific tests with reusable fixtures, so that I can verify database operations and data integrity.

#### Acceptance Criteria

1. THE Test_Suite SHALL provide a Test_Fixture creating sample users
2. THE Test_Suite SHALL provide a Test_Fixture creating sample resumes linked to users
3. THE Test_Suite SHALL provide a Test_Fixture creating sample chat messages
4. THE Test_Suite SHALL test database constraint enforcement (unique email, foreign key cascades)
5. THE Test_Suite SHALL test database transaction rollback behavior
6. THE Test_Suite SHALL test concurrent access scenarios with multiple sessions
7. WHEN tests complete, THE Test_Fixture SHALL clean up all test data
8. THE Test_Suite SHALL use the Test_Database (SQLite in-memory) for all database tests

### Requirement 6: Add Google OAuth Authentication

**User Story:** As a student user, I want to sign in with my Google account, so that I can access the platform without creating a separate password.

#### Acceptance Criteria

1. THE Database_Schema SHALL add an oauth_provider column to the users table (nullable String, values: null, "google")
2. THE Database_Schema SHALL add an oauth_id column to the users table (nullable String, unique when not null)
3. THE Database_Schema SHALL modify hashed_password to be nullable for OAuth users
4. THE OAuth_Module SHALL provide a GET /auth/google/login endpoint redirecting to Google OAuth consent screen
5. THE OAuth_Module SHALL provide a GET /auth/google/callback endpoint handling OAuth code exchange
6. WHEN a user authenticates via Google, THE OAuth_Module SHALL store their Google ID, email, name, and avatar_url
7. WHEN a Google email already exists with password authentication, THE OAuth_Module SHALL link the accounts
8. WHEN Google authentication succeeds, THE OAuth_Module SHALL return a JWT access_token identical to password authentication
9. THE OAuth_Module SHALL validate OAuth state parameter to prevent CSRF attacks
10. WHEN OAuth callback receives an error, THE OAuth_Module SHALL return a descriptive error message

### Requirement 7: Create Optional Projects Database Table

**User Story:** As a student user, I want my projects stored in a dedicated database table, so that I can manage a structured portfolio with full CRUD capabilities.

#### Acceptance Criteria

1. THE Database_Schema SHALL create a projects table with columns: id (UUID, primary key), user_id (UUID, foreign key to users with CASCADE delete), title (String 200), description (Text), tech_stack (JSON array), github_url (Text, nullable), live_url (Text, nullable), thumbnail_url (Text, nullable), created_at (DateTime), updated_at (DateTime)
2. THE Migration_System SHALL generate a migration creating the projects table
3. WHEN a user is deleted, THE Database_Schema SHALL cascade delete all associated projects
4. THE Database_Schema SHALL index user_id for efficient project queries

### Requirement 8: Create Projects API Endpoints

**User Story:** As a student user, I want API endpoints to manage my projects, so that I can create, read, update, and delete my portfolio items.

#### Acceptance Criteria

1. THE API_Endpoints SHALL provide POST /projects creating a new project for the authenticated user
2. THE API_Endpoints SHALL provide GET /projects listing all projects for the authenticated user
3. THE API_Endpoints SHALL provide GET /projects/{project_id} retrieving a specific project
4. THE API_Endpoints SHALL provide PUT /projects/{project_id} updating a project owned by the authenticated user
5. THE API_Endpoints SHALL provide DELETE /projects/{project_id} deleting a project owned by the authenticated user
6. WHEN a user attempts to access another user's project, THE API_Endpoints SHALL return 403 Forbidden
7. WHEN a project is not found, THE API_Endpoints SHALL return 404 Not Found
8. THE API_Endpoints SHALL validate required fields (title, description) on creation and update
9. THE API_Endpoints SHALL validate tech_stack as a JSON array of strings

### Requirement 9: Create Mock Tests for External APIs

**User Story:** As a developer, I want mock tests for external API interactions, so that tests run reliably without network dependencies.

#### Acceptance Criteria

1. THE Test_Suite SHALL mock Groq_API responses for chat completions
2. THE Test_Suite SHALL mock Groq_API responses for resume analysis
3. THE Test_Suite SHALL mock Groq_API responses for roadmap generation
4. THE Test_Suite SHALL mock Groq_API responses for interview feedback
5. THE Test_Suite SHALL mock GitHub_API responses for user profile retrieval
6. THE Test_Suite SHALL mock GitHub_API responses for repository listing
7. THE Test_Suite SHALL mock GitHub_API responses for commit history
8. WHEN external API mocks are used, THE Test_Suite SHALL verify correct request parameters
9. WHEN external API mocks simulate errors, THE Test_Suite SHALL verify proper error handling

### Requirement 10: Create Test Coverage Reporting

**User Story:** As a developer, I want test coverage reporting, so that I can identify untested code paths.

#### Acceptance Criteria

1. THE Test_Suite SHALL generate coverage reports showing percentage coverage per module
2. THE Test_Suite SHALL generate coverage reports showing uncovered line numbers
3. THE Test_Suite SHALL generate HTML coverage reports for detailed visualization
4. WHEN coverage drops below 80%, THE Test_Suite SHALL report a warning
5. THE Test_Suite SHALL exclude test files, migrations, and configuration files from coverage calculation

### Requirement 11: Add Alembic Migration Helper Commands

**User Story:** As a developer, I want documented migration commands, so that I can easily generate, apply, and rollback migrations.

#### Acceptance Criteria

1. THE Migration_System SHALL support `alembic revision --autogenerate -m "message"` for generating migrations
2. THE Migration_System SHALL support `alembic upgrade head` for applying all pending migrations
3. THE Migration_System SHALL support `alembic downgrade -1` for rolling back one migration
4. THE Migration_System SHALL support `alembic current` for showing current migration version
5. THE Migration_System SHALL support `alembic history` for showing migration history
6. WHEN autogenerate detects no changes, THE Migration_System SHALL create an empty migration file

### Requirement 12: Implement Test Isolation and Cleanup

**User Story:** As a developer, I want test isolation guarantees, so that test execution order doesn't affect results.

#### Acceptance Criteria

1. THE Test_Suite SHALL reset the Test_Database to a clean state before each test
2. THE Test_Suite SHALL use Test_Fixtures with function scope for isolated data
3. WHEN a test creates data, THE Test_Suite SHALL ensure it doesn't affect subsequent tests
4. THE Test_Suite SHALL support parallel test execution without conflicts
5. WHEN tests complete, THE Test_Suite SHALL close all database connections

### Requirement 13: Add Authentication Tests with JWT Tokens

**User Story:** As a developer, I want tests verifying JWT authentication, so that I can ensure secure endpoint protection.

#### Acceptance Criteria

1. THE Test_Suite SHALL test accessing protected endpoints without a token returns 401
2. THE Test_Suite SHALL test accessing protected endpoints with an invalid token returns 401
3. THE Test_Suite SHALL test accessing protected endpoints with an expired token returns 401
4. THE Test_Suite SHALL test accessing protected endpoints with a valid token succeeds
5. THE Test_Suite SHALL provide a Test_Fixture generating valid JWT tokens for authenticated tests
6. WHEN a token is generated for a user, THE Test_Suite SHALL verify it contains correct user_id claims

### Requirement 14: Add Performance and Load Tests

**User Story:** As a developer, I want performance tests for critical endpoints, so that I can identify bottlenecks and ensure acceptable response times.

#### Acceptance Criteria

1. THE Test_Suite SHALL test resume upload and analysis completes within 10 seconds for 5MB files
2. THE Test_Suite SHALL test chat message retrieval completes within 500ms for 100 messages
3. THE Test_Suite SHALL test roadmap generation completes within 15 seconds
4. THE Test_Suite SHALL test GitHub analysis completes within 20 seconds for profiles with 50 repositories
5. WHEN concurrent requests exceed 10, THE Test_Suite SHALL verify all requests complete successfully

### Requirement 15: Create Test Documentation

**User Story:** As a developer, I want test documentation, so that I understand how to run tests and interpret results.

#### Acceptance Criteria

1. THE Test_Suite SHALL provide a README documenting test execution commands
2. THE Test_Suite SHALL provide documentation explaining test organization and structure
3. THE Test_Suite SHALL provide documentation for writing new tests
4. THE Test_Suite SHALL provide documentation for Test_Fixtures usage
5. THE Test_Suite SHALL provide documentation for running specific test categories (unit, integration, database)
