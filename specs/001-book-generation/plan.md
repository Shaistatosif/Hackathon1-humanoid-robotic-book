# Implementation Plan: Book Generation

**Branch**: `001-book-generation` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-book-generation/spec.md`

## Summary

Build an AI-native humanoid robotics textbook platform using Docusaurus for content presentation,
FastAPI backend with Gemini 2.5 Flash for AI operations, Qdrant Cloud for RAG vector search,
and BetterAuth for user authentication. The system delivers educational content with interactive
Q&A chatbot, Urdu translation with RTL support, chapter quizzes, summaries, and personalized
learning dashboard.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend)
**Primary Dependencies**: Docusaurus 3.x, FastAPI, Gemini 2.5 Flash API, Qdrant Cloud, BetterAuth
**Storage**: Qdrant Cloud (vectors), SQLite/PostgreSQL (user data), Markdown files (content)
**Testing**: Vitest (frontend), pytest (backend)
**Target Platform**: Web (modern browsers), Linux server deployment
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <2s page load, <5s RAG response, 100 concurrent users
**Constraints**: <2s RAG queries, WCAG AA compliance, RTL layout support
**Scale/Scope**: ~10-15 chapters, 100+ concurrent users, 2 languages (EN/UR)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Deterministic Outputs | ✅ PASS | Structured content from Markdown, reproducible RAG with temperature=0 |
| II. No Hallucinations | ✅ PASS | RAG grounded in textbook content, citations required, out-of-scope acknowledgment |
| III. Traceability | ✅ PASS | Spec → Plan → Tasks workflow, PHR documentation |
| IV. Academic Clarity | ✅ PASS | Docusaurus typography, syntax highlighting, professional layout |
| V. Modular Architecture | ✅ PASS | Separate frontend/backend, isolated agent responsibilities |
| VI. RAG Accuracy | ✅ PASS | Sentence-aware chunking, mandatory citations, scope awareness |
| VII. Translation Fidelity | ✅ PASS | Code blocks excluded, RTL mode, transliteration support |
| VIII. Hackathon Compliance | ✅ PASS | All bonus features in scope (subagents, personalization, Urdu, BetterAuth, RAG, quizzes, summaries, dashboard, MCP) |

**Technical Constraints Compliance:**

| Constraint | Status | Implementation |
|------------|--------|----------------|
| Frontend: Docusaurus | ✅ | Primary content platform |
| Frontend: Urdu RTL | ✅ | i18n with RTL CSS |
| Frontend: WCAG AA | ✅ | Accessibility audit in acceptance criteria |
| Backend: FastAPI | ✅ | API layer for RAG, auth, user data |
| Backend: Gemini 2.5 Flash | ✅ | LLM for RAG, quiz generation, summaries |
| Backend: Qdrant Cloud | ✅ | Vector storage for RAG embeddings |
| Security: BetterAuth | ✅ | Authentication system |
| Security: No hardcoded secrets | ✅ | Environment variables |

## Project Structure

### Documentation (this feature)

```text
specs/001-book-generation/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity schemas
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API specifications
│   ├── rag-api.yaml     # RAG chatbot endpoints
│   ├── auth-api.yaml    # Authentication endpoints
│   ├── user-api.yaml    # User data endpoints
│   └── quiz-api.yaml    # Quiz endpoints
└── tasks.md             # Phase 2: Implementation tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # Pydantic models, database schemas
│   │   ├── user.py
│   │   ├── chapter.py
│   │   ├── quiz.py
│   │   └── chat.py
│   ├── services/        # Business logic
│   │   ├── rag_service.py
│   │   ├── auth_service.py
│   │   ├── quiz_service.py
│   │   ├── summary_service.py
│   │   └── progress_service.py
│   ├── api/             # FastAPI routers
│   │   ├── rag.py
│   │   ├── auth.py
│   │   ├── quiz.py
│   │   └── user.py
│   ├── core/            # Configuration, dependencies
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   └── main.py          # FastAPI app entry point
├── scripts/
│   ├── ingest_content.py    # Chunk and embed textbook content
│   └── generate_quizzes.py  # Generate quizzes from chapters
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

frontend/
├── docusaurus.config.ts     # Docusaurus configuration
├── i18n/
│   ├── en/                  # English content
│   └── ur/                  # Urdu translations
├── src/
│   ├── components/
│   │   ├── ChatWidget/      # RAG chatbot UI
│   │   ├── Quiz/            # Quiz components
│   │   ├── Dashboard/       # User dashboard
│   │   ├── LanguageToggle/  # EN/UR switcher
│   │   └── Summary/         # Chapter summary display
│   ├── pages/
│   │   ├── dashboard.tsx    # Personalized dashboard
│   │   └── login.tsx        # Auth pages
│   ├── services/
│   │   ├── api.ts           # Backend API client
│   │   └── auth.ts          # BetterAuth client
│   └── css/
│       └── rtl.css          # RTL layout styles
├── docs/                    # Textbook content (Markdown)
│   ├── intro.md
│   ├── chapter-1/
│   ├── chapter-2/
│   └── ...
├── static/
│   └── img/                 # Diagrams, images
└── tests/
    └── e2e/

content/
├── source/                  # Original English textbook content
│   ├── chapter-1.md
│   ├── chapter-2.md
│   └── ...
└── translations/
    └── ur/                  # Urdu translations
        ├── chapter-1.md
        └── ...
```

**Structure Decision**: Web application architecture with separate frontend (Docusaurus + React components)
and backend (FastAPI). Content stored as Markdown files, processed for RAG indexing. This separation
allows independent deployment and scaling of content delivery vs API services.

## Complexity Tracking

No constitution violations requiring justification. Architecture follows established patterns:
- Frontend/backend separation (standard web app)
- Docusaurus for documentation sites (official recommendation)
- FastAPI for Python APIs (industry standard)
- Qdrant for vector search (purpose-built)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Docusaurus)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Textbook │  │ Chat     │  │ Quiz     │  │ Dashboard        │ │
│  │ Content  │  │ Widget   │  │ Component│  │ (Personalization)│ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              i18n (EN/UR with RTL support)               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ RAG Service  │  │ Auth Service │  │ Quiz Service │           │
│  │ (Gemini +    │  │ (BetterAuth) │  │ (Generation +│           │
│  │  Qdrant)     │  │              │  │  Scoring)    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ Summary      │  │ Progress     │                             │
│  │ Service      │  │ Service      │                             │
│  └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │ Qdrant   │   │ SQLite/  │   │ Gemini 2.5   │
        │ Cloud    │   │ Postgres │   │ Flash API    │
        │ (Vectors)│   │ (Users)  │   │ (LLM)        │
        └──────────┘   └──────────┘   └──────────────┘
```

## Data Flow

### RAG Query Flow

```
User Question → Chat Widget → Backend /api/rag/query
    → Embed question (Gemini)
    → Search Qdrant (top-k chunks)
    → Generate answer with citations (Gemini)
    → Return answer + citations → Chat Widget → User
```

### Content Ingestion Flow

```
Markdown Content → ingest_content.py
    → Split into chunks (sentence-aware)
    → Generate embeddings (Gemini)
    → Store in Qdrant with metadata (chapter, section)
```

### Quiz Flow

```
Chapter Content → generate_quizzes.py
    → Generate questions (Gemini)
    → Store quiz in database
User takes quiz → Quiz Component → Backend /api/quiz/submit
    → Score answers → Store attempt → Return results
```
