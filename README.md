# SkillBridge AI 🚀

**AI-Powered Career Mentoring Platform for Students and Fresh Graduates**

SkillBridge AI is a comprehensive career development platform that leverages artificial intelligence to help students and fresh graduates accelerate their career growth through personalized guidance, skill assessment, and learning roadmaps.

## ✨ Features

### 🎯 Core Features
- **AI Career Mentor** - Chat with an AI mentor powered by Groq (Llama 3.3 70B) for personalized career guidance
- **Resume Analyzer** - Upload your resume for AI-powered analysis with ATS scoring and improvement suggestions
- **Learning Roadmaps** - Generate personalized learning paths based on your career goals and current skills
- **GitHub Profile Analyzer** - Get detailed analysis of your GitHub profile with actionable suggestions
- **Mock Interviews** - Practice technical interviews with AI-generated questions and feedback
- **Progress Tracker** - Track your learning journey and skill development
- **Job Matching** - Find relevant job opportunities based on your skills and preferences

### 🔧 Technical Features
- **RAG (Retrieval-Augmented Generation)** - Context-aware responses using ChromaDB vector database
- **Real-time Streaming** - Server-Sent Events for smooth AI response streaming
- **Authentication** - Secure JWT-based authentication with Argon2 password hashing
- **Database Migrations** - Alembic for database version control
- **Comprehensive Testing** - Unit and integration tests with pytest

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **SQLAlchemy** - ORM with async support
- **Alembic** - Database migration tool
- **Groq API** - LLM inference (Llama 3.3 70B Versatile)
- **ChromaDB** - Vector database for RAG
- **Argon2** - Secure password hashing
- **PyMuPDF** - PDF parsing for resume analysis
- **Pytest** - Testing framework

### Frontend
- **Next.js 16** - React framework with Turbopack
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Lucide React** - Icon library

### Database
- **PostgreSQL** - Production database (async with asyncpg)
- **SQLite** - Development/testing database (async with aiosqlite)

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/abhisheksinghcodebase/Skillbridge-AI.git
   cd Skillbridge-AI/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local if needed
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   ```
   http://localhost:3000
   ```

## 🔑 API Keys

You'll need the following API keys:

- **Groq API Key** (Required) - Get free key at [console.groq.com](https://console.groq.com)
- **GitHub Token** (Optional) - For GitHub profile analysis

Add these to your `backend/.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_token_here  # Optional
```

## 🚀 Usage

1. **Register/Login** - Create an account or login
2. **Upload Resume** - Get AI-powered resume analysis
3. **Generate Roadmap** - Create personalized learning paths
4. **Chat with Mentor** - Ask career-related questions
5. **Analyze GitHub** - Get profile improvement suggestions
6. **Practice Interviews** - Prepare with AI-generated questions
7. **Track Progress** - Monitor your learning journey

## 📊 Project Structure

```
Skillbridge-AI/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/routers/      # API endpoints
│   │   ├── core/             # Configuration & security
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── main.py           # FastAPI application
│   ├── tests/                # Test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── (dashboard)/      # Dashboard pages
│   │   ├── auth/             # Authentication pages
│   │   └── layout.tsx
│   ├── lib/                  # Utilities & API client
│   ├── contexts/             # React contexts
│   ├── package.json
│   └── .env.example
└── README.md
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest tests/unit/       # All unit tests
```

### Test Coverage
- Unit tests for all service layers
- Integration tests for API endpoints
- Database constraint and transaction tests
- 80%+ code coverage target

## 🔒 Security Features

- **Argon2** password hashing (winner of Password Hashing Competition)
- **JWT** token-based authentication
- **CORS** protection
- **Input validation** with Pydantic
- **SQL injection** protection via SQLAlchemy ORM
- **Rate limiting** ready (can be configured)

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Abhishek Singh**
- GitHub: [@abhisheksinghcodebase](https://github.com/abhisheksinghcodebase)

## 🙏 Acknowledgments

- Groq for providing fast LLM inference
- FastAPI team for the amazing framework
- Next.js team for the incredible developer experience
- All open-source contributors

## 📧 Support

For support, email abhisheksinghcodebase@gmail.com or open an issue on GitHub.

---

⭐ **Star this repo if you find it helpful!** ⭐
