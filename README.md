# Humanoid Robotics Interactive Textbook

An AI-native educational platform for learning humanoid robotics, featuring bilingual content (English/Urdu), RAG-powered chatbot, interactive quizzes, and personalized learning dashboards.

## Features

- **Interactive Textbook**: Navigate through chapters covering humanoid robotics fundamentals
- **RAG Chatbot**: Ask questions and get answers with citations from the textbook
- **Bilingual Support**: Full Urdu translation with RTL layout
- **Chapter Quizzes**: Test your understanding with AI-generated quizzes
- **Chapter Summaries**: AI-generated bullet-point summaries of key concepts
- **Personalized Dashboard**: Track reading progress, quiz scores, and bookmarks
- **Authentication**: Secure user accounts with JWT-based authentication

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy** - Async ORM with SQLite
- **Qdrant** - Vector database for RAG
- **Google Gemini** - AI for embeddings and generation

### Frontend
- **Docusaurus 3** - Documentation-focused React framework
- **TypeScript** - Type-safe JavaScript
- **React 18** - UI components

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# - GEMINI_API_KEY
# - QDRANT_URL (optional)
# - QDRANT_API_KEY (optional)

# Run the server
uvicorn src.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with API URL

# Run development server
npm run start
```

Frontend will be available at http://localhost:3000

## Project Structure

```
humanoid-robotics-textbook/
├── backend/
│   ├── src/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration, database, clients
│   │   ├── models/       # SQLAlchemy models
│   │   └── services/     # Business logic
│   ├── scripts/          # Content ingestion scripts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── context/      # React context providers
│   │   ├── hooks/        # Custom React hooks
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── theme/        # Docusaurus theme overrides
│   ├── docs/             # Textbook content (markdown)
│   └── i18n/             # Translations
├── content/
│   ├── source/           # English content
│   ├── translations/     # Urdu translations
│   └── quizzes/          # Generated quiz data
└── specs/                # Feature specifications
```

## API Documentation

When running in development mode, API docs are available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login and get JWT token |
| `/api/rag/query` | POST | Ask RAG chatbot a question |
| `/api/quiz/chapter/{id}` | GET | Get quiz for a chapter |
| `/api/user/dashboard` | GET | Get personalized dashboard |
| `/api/health/detailed` | GET | Health check with dependencies |

## Environment Variables

### Backend (.env)

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional - Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# Optional - Database (defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# Optional - Auth
BETTER_AUTH_SECRET=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Optional - Debug
DEBUG=true
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## Content Management

### Ingesting Content

```bash
cd backend

# Ingest English content into Qdrant
python scripts/ingest_content.py

# Ingest Urdu content
python scripts/ingest_content.py --language ur
```

### Generating Quizzes

```bash
cd backend
python scripts/generate_quizzes.py
```

### Generating Summaries

```bash
cd backend
python scripts/generate_summaries.py
```

## Deployment

### Backend (Docker)

```bash
cd backend
docker build -t humanoid-robotics-api .
docker run -p 8000:8000 --env-file .env humanoid-robotics-api
```

### Frontend (Vercel)

The frontend is configured for Vercel deployment. Connect your repository to Vercel and it will automatically deploy.

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the AI-native hackathon
- Uses Google Gemini for AI capabilities
- Powered by Docusaurus for documentation
