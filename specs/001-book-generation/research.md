# Research: Book Generation

**Feature**: 001-book-generation
**Date**: 2025-12-17
**Status**: Complete

## Research Areas

### 1. Docusaurus i18n and RTL Support

**Decision**: Use Docusaurus built-in i18n with CSS RTL utilities

**Rationale**:
- Docusaurus 3.x has native internationalization support
- RTL can be handled via `dir="rtl"` attribute and CSS logical properties
- No additional libraries needed for basic RTL layout

**Alternatives Considered**:
- Custom React i18n library: Rejected (unnecessary complexity, Docusaurus handles this)
- Separate Urdu site: Rejected (harder to maintain, violates DRY)

**Implementation Notes**:
- Configure `i18n` in `docusaurus.config.ts` with locales: ['en', 'ur']
- Add `dir="rtl"` conditionally for Urdu locale
- Use `margin-inline-start`/`margin-inline-end` instead of `margin-left`/`margin-right`

---

### 2. RAG Architecture with Gemini and Qdrant

**Decision**: Gemini embeddings → Qdrant Cloud → Gemini 2.5 Flash generation

**Rationale**:
- Gemini API provides both embeddings and generation in one ecosystem
- Qdrant Cloud offers managed vector database (no infrastructure management)
- Sentence-aware chunking preserves meaning per constitution requirement

**Alternatives Considered**:
- OpenAI embeddings + GPT-4: Rejected (constitution mandates Gemini)
- Pinecone: Rejected (Qdrant specified in constitution)
- Local Qdrant: Rejected (Cloud reduces DevOps burden for hackathon)

**Implementation Notes**:
- Embedding model: `text-embedding-004` (768 dimensions)
- Chunk size: ~500 tokens with sentence boundary detection
- Top-k retrieval: 5 chunks for context
- Temperature: 0 for reproducible outputs

---

### 3. BetterAuth Integration

**Decision**: BetterAuth with email/password and session-based auth

**Rationale**:
- Constitution mandates BetterAuth
- Email/password is simplest for hackathon scope
- Session-based auth works well with server-rendered Docusaurus

**Alternatives Considered**:
- NextAuth: Rejected (BetterAuth specified)
- OAuth only: Rejected (email/password is more accessible)
- JWT tokens: Rejected (session-based simpler for this use case)

**Implementation Notes**:
- Backend integration with FastAPI
- Frontend auth context for React components
- Secure httpOnly cookies for session

---

### 4. Quiz Generation Strategy

**Decision**: Pre-generate quizzes during content ingestion, store in database

**Rationale**:
- Faster quiz access (no LLM call at runtime)
- Consistent questions for all users
- Allows review/editing of generated questions

**Alternatives Considered**:
- Runtime generation: Rejected (slower, inconsistent, higher API costs)
- Manual quiz creation: Rejected (doesn't scale, defeats AI-native purpose)

**Implementation Notes**:
- Generate 5-10 questions per chapter
- Mix of multiple-choice (80%) and short-answer (20%)
- Store in SQLite/PostgreSQL with chapter foreign key

---

### 5. Summary Generation Strategy

**Decision**: Pre-generate summaries during content ingestion, cache in database

**Rationale**:
- Same benefits as quiz pre-generation
- Summaries are static per chapter (content doesn't change)
- Reduces LLM API calls and latency

**Alternatives Considered**:
- Runtime generation with caching: Rejected (cold start latency)
- Manual summaries: Rejected (doesn't scale)

**Implementation Notes**:
- Generate 5-7 bullet points per chapter
- Include key terms and concepts
- Store alongside chapter metadata

---

### 6. Urdu Translation Approach

**Decision**: AI-assisted translation with human review markers

**Rationale**:
- Full manual translation not feasible in hackathon timeline
- Gemini can translate while preserving technical terms
- Mark translations as "AI-generated" for transparency

**Alternatives Considered**:
- Google Translate API: Rejected (less control over technical terms)
- Manual translation: Rejected (timeline constraints)
- No translation: Rejected (constitution requires Urdu)

**Implementation Notes**:
- Translate chapter-by-chapter via script
- Keep English technical terms with Urdu transliteration: `robot (روبوٹ)`
- Exclude code blocks from translation (regex detection)

---

### 7. Personalization Engine

**Decision**: Simple rule-based recommendations based on progress

**Rationale**:
- Full ML-based personalization overkill for hackathon
- Progress-based recommendations are intuitive and testable
- Meets constitution requirement without over-engineering

**Alternatives Considered**:
- Collaborative filtering: Rejected (needs user base data)
- Content-based ML: Rejected (complexity vs. value)

**Implementation Notes**:
- Track chapters read, quizzes completed, time spent
- Recommend: next sequential chapter, or retry low-scoring quizzes
- Show progress percentage on dashboard

---

### 8. Database Choice

**Decision**: SQLite for development, PostgreSQL option for production

**Rationale**:
- SQLite is zero-config, perfect for hackathon demo
- Schema works identically with PostgreSQL if needed
- Content vectors in Qdrant, user data in relational DB

**Alternatives Considered**:
- MongoDB: Rejected (relational model fits better)
- PostgreSQL only: Rejected (SQLite simpler for demo)

**Implementation Notes**:
- Use SQLAlchemy for ORM (portable across SQLite/PostgreSQL)
- Tables: users, quiz_attempts, reading_progress, bookmarks
- Foreign keys to chapter IDs (stored as strings matching content)

---

### 9. Content Structure

**Decision**: Markdown files organized by chapter in `content/source/` directory

**Rationale**:
- Markdown is native to Docusaurus
- Easy to version control and edit
- Can be processed for RAG ingestion

**Alternatives Considered**:
- CMS (Contentful, Strapi): Rejected (unnecessary complexity)
- Database storage: Rejected (harder to edit, version)

**Implementation Notes**:
- Each chapter is a directory with `index.md` and section files
- Front matter includes: title, order, description
- Images stored in `static/img/chapters/`

---

### 10. Deployment Strategy

**Decision**: Vercel (frontend) + Railway/Render (backend) + Qdrant Cloud

**Rationale**:
- Vercel optimal for Docusaurus static + serverless
- Railway/Render simple for FastAPI deployment
- Qdrant Cloud is managed (no self-hosting)

**Alternatives Considered**:
- Self-hosted VPS: Rejected (more DevOps work)
- Docker Compose: Rejected (adds complexity for hackathon)

**Implementation Notes**:
- Frontend: `vercel deploy` from `frontend/` directory
- Backend: Docker container on Railway/Render
- Environment variables for API keys, database URLs

## Summary of Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Docusaurus 3.x | Textbook content, navigation |
| Frontend Components | React + TypeScript | Chat widget, quiz, dashboard |
| Backend | FastAPI (Python 3.11+) | API layer |
| LLM | Gemini 2.5 Flash | RAG, quiz generation, summaries, translation |
| Vector DB | Qdrant Cloud | RAG embeddings storage |
| Relational DB | SQLite (dev) / PostgreSQL (prod) | User data, quiz attempts |
| Auth | BetterAuth | User authentication |
| i18n | Docusaurus i18n | English/Urdu support |
| Deployment | Vercel + Railway + Qdrant Cloud | Hosting |

## Open Questions Resolved

All technical decisions have been made. No NEEDS CLARIFICATION items remain.
