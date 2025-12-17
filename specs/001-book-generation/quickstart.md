# Quickstart Guide: Book Generation

**Feature**: 001-book-generation
**Date**: 2025-12-17

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Git
- Qdrant Cloud account (free tier available)
- Google Cloud account with Gemini API access

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd hackathon-one-humanoid-robotic-book
git checkout 001-book-generation
```

### 2. Create Environment Files

**Backend (.env)**

Create `backend/.env`:

```env
# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.cloud:6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=textbook_chunks

# Database
DATABASE_URL=sqlite:///./app.db

# BetterAuth
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:8000

# Email (for verification - use Resend or similar)
EMAIL_API_KEY=your-email-api-key
EMAIL_FROM=noreply@yourdomain.com

# CORS
FRONTEND_URL=http://localhost:3000
```

**Frontend (.env)**

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api
VITE_SITE_URL=http://localhost:3000
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.core.database import init_db; init_db()"

# Run backend server
uvicorn src.main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run start
```

### 5. Content Ingestion (One-time)

```bash
cd backend

# Ingest textbook content into Qdrant
python scripts/ingest_content.py --content-dir ../content/source

# Generate quizzes for each chapter
python scripts/generate_quizzes.py

# Generate summaries for each chapter
python scripts/generate_summaries.py
```

## Verify Setup

### Backend Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "1.0.0"}
```

### Frontend Access

Open http://localhost:3000 in your browser. You should see:
- Textbook homepage with table of contents
- Language toggle (EN/UR)
- Chat widget button

### RAG Query Test

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are humanoid robots?"}'
```

Expected response includes:
- `answer`: Generated text
- `citations`: Array with chapter references
- `is_in_scope`: true

## Development Workflow

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/ -v
```

**Frontend:**
```bash
cd frontend
npm run test
```

### Adding New Content

1. Add markdown file to `content/source/chapter-X/`
2. Run ingestion script: `python scripts/ingest_content.py --chapter chapter-X`
3. Generate quiz: `python scripts/generate_quizzes.py --chapter chapter-X`
4. Generate summary: `python scripts/generate_summaries.py --chapter chapter-X`

### Adding Urdu Translation

1. Add translated markdown to `content/translations/ur/chapter-X.md`
2. Re-run ingestion with language flag: `python scripts/ingest_content.py --chapter chapter-X --language ur`

## Common Issues

### Qdrant Connection Error

```
Error: Failed to connect to Qdrant
```

Solution: Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`. Ensure your IP is whitelisted in Qdrant Cloud.

### Gemini API Rate Limit

```
Error: 429 Too Many Requests
```

Solution: Reduce batch size in ingestion scripts or wait for rate limit reset.

### CORS Error in Browser

```
Error: Access-Control-Allow-Origin
```

Solution: Verify `FRONTEND_URL` in backend `.env` matches your frontend URL exactly.

### RTL Not Rendering

If Urdu text doesn't render right-to-left:
1. Check browser supports RTL
2. Verify `dir="rtl"` is set on `<html>` element
3. Check CSS logical properties are used

## Project Structure

```
hackathon-one-humanoid-robotic-book/
├── backend/
│   ├── src/
│   │   ├── api/           # FastAPI routers
│   │   ├── core/          # Config, database
│   │   ├── models/        # Pydantic models
│   │   └── services/      # Business logic
│   ├── scripts/           # Ingestion scripts
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── docs/              # Textbook content
│   ├── i18n/              # Translations
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Custom pages
│   │   └── services/      # API client
│   └── docusaurus.config.ts
├── content/
│   ├── source/            # English markdown
│   └── translations/ur/   # Urdu markdown
└── specs/
    └── 001-book-generation/
```

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement tasks in priority order (P1 → P7)
3. Test each user story independently
4. Deploy to Vercel (frontend) and Railway (backend)
