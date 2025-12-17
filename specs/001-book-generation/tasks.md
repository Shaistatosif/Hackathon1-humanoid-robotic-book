# Tasks: Book Generation

**Input**: Design documents from `/specs/001-book-generation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. Test tasks are omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/docs/`
- **Content**: `content/source/`, `content/translations/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and initialize dependencies

- [x] T001 Create backend directory structure per plan.md in backend/
- [x] T002 Create frontend directory structure per plan.md in frontend/
- [x] T003 Create content directory structure in content/source/ and content/translations/ur/
- [x] T004 [P] Initialize Python project with pyproject.toml in backend/
- [x] T005 [P] Initialize Docusaurus project with npm init docusaurus in frontend/
- [x] T006 [P] Create backend requirements.txt with FastAPI, SQLAlchemy, Qdrant-client, google-generativeai, python-dotenv, uvicorn, better-auth
- [x] T007 [P] Create backend .env.example with GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET placeholders
- [x] T008 [P] Create frontend .env.example with VITE_API_URL placeholder
- [x] T009 Configure ESLint and Prettier for frontend in frontend/.eslintrc.js and frontend/.prettierrc
- [x] T010 Configure Ruff linter for backend in backend/pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 Create FastAPI app entry point with CORS middleware in backend/src/main.py
- [x] T012 Create configuration module loading env vars in backend/src/core/config.py
- [x] T013 Create SQLAlchemy database setup with SQLite in backend/src/core/database.py
- [x] T014 Create Qdrant client singleton in backend/src/core/qdrant.py
- [x] T015 Create Gemini client wrapper in backend/src/core/gemini.py
- [x] T016 [P] Create User model with SQLAlchemy in backend/src/models/user.py
- [x] T017 [P] Create Chapter model (metadata only) in backend/src/models/chapter.py
- [x] T018 Create BetterAuth integration service in backend/src/services/auth_service.py
- [x] T019 Create auth API router with register/login/logout/verify endpoints in backend/src/api/auth.py
- [x] T020 Create security middleware for protected routes in backend/src/core/security.py
- [x] T021 Configure Docusaurus with TypeScript in frontend/docusaurus.config.ts
- [x] T022 Create API client service with fetch wrapper in frontend/src/services/api.ts
- [x] T023 Create BetterAuth client for frontend in frontend/src/services/auth.ts
- [x] T024 Create AuthContext provider for React components in frontend/src/context/AuthContext.tsx
- [x] T025 Create Login page component in frontend/src/pages/login.tsx
- [x] T026 Create Register page component in frontend/src/pages/register.tsx
- [x] T027 Run database migrations to create users table via backend/src/core/database.py init

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Browse Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Users can navigate through chapters and read humanoid robotics content with professional typography

**Independent Test**: Navigate to homepage, browse TOC, read any chapter, verify navigation works

### Implementation for User Story 1

- [x] T028 [US1] Create sample Chapter 1 content in content/source/chapter-1/index.md with intro to humanoid robotics
- [x] T029 [P] [US1] Create sample Chapter 2 content in content/source/chapter-2/index.md with robot components
- [x] T030 [P] [US1] Create sample Chapter 3 content in content/source/chapter-3/index.md with sensors and actuators
- [x] T031 [US1] Create Docusaurus sidebar configuration with chapter hierarchy in frontend/sidebars.ts
- [x] T032 [US1] Copy content from content/source/ to frontend/docs/ with proper structure
- [x] T033 [US1] Configure Docusaurus theme for professional typography in frontend/src/css/custom.css
- [x] T034 [US1] Add syntax highlighting for code blocks in docusaurus.config.ts prism configuration
- [x] T035 [US1] Create chapter navigation component (prev/next) in frontend/src/components/ChapterNav/index.tsx
- [x] T036 [US1] Add search functionality using Docusaurus local search plugin in docusaurus.config.ts
- [x] T037 [US1] Configure homepage with intro and table of contents link in frontend/src/pages/index.tsx
- [x] T038 [US1] Add responsive styles for desktop and tablet in frontend/src/css/custom.css

**Checkpoint**: User Story 1 complete - textbook is browsable with professional layout

---

## Phase 4: User Story 2 - RAG Chatbot (Priority: P2)

**Goal**: Users can ask questions and receive accurate answers with citations from textbook content

**Independent Test**: Open chatbot, ask "What are humanoid robots?", receive answer with chapter citation

### Implementation for User Story 2

- [x] T039 [US2] Create content chunking script with sentence-aware splitting in backend/scripts/ingest_content.py
- [x] T040 [US2] Implement embedding generation using Gemini text-embedding-004 in backend/scripts/ingest_content.py
- [x] T041 [US2] Create Qdrant collection and upsert chunks in backend/scripts/ingest_content.py
- [x] T042 [US2] Run ingest_content.py to populate Qdrant with English content
- [x] T043 [US2] Create ChatSession model in backend/src/models/chat.py
- [x] T044 [P] [US2] Create ChatMessage model in backend/src/models/chat.py
- [x] T045 [US2] Create RAG service with query embedding and Qdrant search in backend/src/services/rag_service.py
- [x] T046 [US2] Implement answer generation with citations using Gemini in backend/src/services/rag_service.py
- [x] T047 [US2] Add out-of-scope detection in RAG service in backend/src/services/rag_service.py
- [x] T048 [US2] Create RAG API router with /query endpoint in backend/src/api/rag.py
- [x] T049 [P] [US2] Create session management endpoints in backend/src/api/rag.py
- [x] T050 [US2] Create ChatWidget component with message input in frontend/src/components/ChatWidget/index.tsx
- [x] T051 [US2] Create ChatMessage component with citation links in frontend/src/components/ChatWidget/ChatMessage.tsx
- [x] T052 [US2] Add ChatWidget to Docusaurus layout as floating button in frontend/src/theme/Root.tsx
- [x] T053 [US2] Implement citation click navigation to chapter section in frontend/src/components/ChatWidget/index.tsx

**Checkpoint**: User Story 2 complete - RAG chatbot answers questions with citations

---

## Phase 5: User Story 3 - Urdu Translation (Priority: P3)

**Goal**: Users can switch to Urdu with proper RTL layout while code blocks remain English

**Independent Test**: Switch to Urdu, verify RTL layout, confirm code blocks are English

### Implementation for User Story 3

- [x] T054 [US3] Create translation script using Gemini for Urdu in backend/scripts/translate_content.py
- [x] T055 [US3] Implement code block preservation in translation script in backend/scripts/translate_content.py
- [x] T056 [US3] Run translation script to generate content/translations/ur/ files
- [x] T057 [US3] Configure Docusaurus i18n with en and ur locales in frontend/docusaurus.config.ts
- [x] T058 [US3] Create Urdu translations directory structure in frontend/i18n/ur/
- [x] T059 [US3] Copy translated content to frontend/i18n/ur/docusaurus-plugin-content-docs/
- [x] T060 [US3] Create RTL stylesheet with logical properties in frontend/src/css/rtl.css
- [x] T061 [US3] Create LanguageToggle component in frontend/src/components/LanguageToggle/index.tsx
- [x] T062 [US3] Add LanguageToggle to navbar in docusaurus.config.ts
- [x] T063 [US3] Implement RTL direction switching based on locale in frontend/src/theme/Root.tsx
- [x] T064 [US3] Ingest Urdu content into Qdrant for bilingual RAG via backend/scripts/ingest_content.py --language ur

**Checkpoint**: User Story 3 complete - Urdu translation with RTL works correctly

---

## Phase 6: User Story 4 - Chapter Quizzes (Priority: P4)

**Goal**: Users can take chapter quizzes and see scores with correct answers

**Independent Test**: Complete a chapter, access quiz, answer questions, view results

### Implementation for User Story 4

- [x] T065 [US4] Create Quiz model in backend/src/models/quiz.py
- [x] T066 [P] [US4] Create Question model in backend/src/models/quiz.py
- [x] T067 [P] [US4] Create QuizAttempt model in backend/src/models/quiz.py
- [x] T068 [US4] Create quiz generation script using Gemini in backend/scripts/generate_quizzes.py
- [x] T069 [US4] Run generate_quizzes.py to create quizzes for all chapters
- [x] T070 [US4] Create quiz service with attempt management in backend/src/services/quiz_service.py
- [x] T071 [US4] Implement answer scoring in quiz service in backend/src/services/quiz_service.py
- [x] T072 [US4] Create quiz API router with get/start/submit endpoints in backend/src/api/quiz.py
- [x] T073 [US4] Create Quiz component with question display in frontend/src/components/Quiz/index.tsx
- [x] T074 [P] [US4] Create QuizQuestion component for MCQ and short answer in frontend/src/components/Quiz/QuizQuestion.tsx
- [x] T075 [P] [US4] Create QuizResults component showing score and answers in frontend/src/components/Quiz/QuizResults.tsx
- [x] T076 [US4] Add quiz access button to chapter pages in frontend/src/components/ChapterNav/index.tsx
- [x] T077 [US4] Create quiz page route in frontend/src/pages/quiz/[chapterId].tsx

**Checkpoint**: User Story 4 complete - quizzes work with scoring and review

---

## Phase 7: User Story 5 - Chapter Summaries (Priority: P5)

**Goal**: Users can view AI-generated chapter summaries with key concepts

**Independent Test**: Navigate to chapter, click summary tab, see bullet-point summary

### Implementation for User Story 5

- [x] T078 [US5] Create summary generation script using Gemini in backend/scripts/generate_summaries.py
- [x] T079 [US5] Run generate_summaries.py to populate Chapter.summary for all chapters
- [x] T080 [US5] Create summary endpoint to fetch chapter summary in backend/src/api/content.py
- [x] T081 [US5] Create Summary component displaying bullet points in frontend/src/components/Summary/index.tsx
- [x] T082 [US5] Add summary tab/section to chapter layout in frontend/src/theme/DocItem/Layout/index.tsx
- [x] T083 [US5] Style summary component for readability in frontend/src/components/Summary/styles.module.css

**Checkpoint**: User Story 5 complete - summaries display key concepts

---

## Phase 8: User Story 6 - Personalized Dashboard (Priority: P6)

**Goal**: Logged-in users see progress, bookmarks, quiz scores, and recommendations

**Independent Test**: Log in, view dashboard, verify progress shows after reading a chapter

### Implementation for User Story 6

- [x] T084 [US6] Create ReadingProgress model in backend/src/models/progress.py
- [x] T085 [P] [US6] Create Bookmark model in backend/src/models/progress.py
- [x] T086 [US6] Create progress service with tracking logic in backend/src/services/progress_service.py
- [x] T087 [US6] Implement recommendation engine based on progress in backend/src/services/progress_service.py
- [x] T088 [US6] Create user API router with progress/bookmarks/dashboard endpoints in backend/src/api/user.py
- [x] T089 [US6] Create Dashboard page component in frontend/src/pages/dashboard.tsx
- [x] T090 [P] [US6] Create ProgressCard component showing completion in frontend/src/components/Dashboard/ProgressCard.tsx
- [x] T091 [P] [US6] Create BookmarksList component in frontend/src/components/Dashboard/BookmarksList.tsx
- [x] T092 [P] [US6] Create QuizHistory component showing past scores in frontend/src/components/Dashboard/QuizHistory.tsx
- [x] T093 [P] [US6] Create Recommendations component in frontend/src/components/Dashboard/Recommendations.tsx
- [x] T094 [US6] Add reading progress tracking on chapter view in frontend/src/hooks/useReadingProgress.ts
- [x] T095 [US6] Add bookmark button to chapter pages in frontend/src/components/BookmarkButton/index.tsx
- [x] T096 [US6] Protect dashboard route for authenticated users in frontend/src/pages/dashboard.tsx

**Checkpoint**: User Story 6 complete - personalized dashboard shows progress and recommendations

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T097 Add error handling middleware in backend/src/main.py
- [x] T098 [P] Add request logging middleware in backend/src/main.py
- [x] T099 [P] Create health check endpoint in backend/src/api/health.py
- [x] T100 Add WCAG AA accessibility attributes to all components in frontend/src/
- [x] T101 [P] Add loading states to all async components in frontend/src/
- [x] T102 [P] Add error boundary wrapper in frontend/src/components/ErrorBoundary/index.tsx
- [x] T103 Create README.md with setup instructions at repository root
- [x] T104 [P] Create backend Dockerfile in backend/Dockerfile
- [x] T105 [P] Configure Vercel deployment for frontend in frontend/vercel.json
- [x] T106 Run accessibility audit and fix issues
- [x] T107 Verify all success criteria from spec.md are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P2 → P3 → P4 → P5 → P6)
  - Some parallelization possible between stories
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

```
US1 (Browse) ─────────────────────────────────────────────────┐
     │                                                         │
     ├── US2 (RAG) depends on US1 content existing             │
     │        │                                                │
     │        └── US3 (Urdu) can run parallel with US2         │
     │                  │                                      │
     │                  └── US4 (Quiz) depends on content      │
     │                            │                            │
     │                            └── US5 (Summary) parallel   │
     │                                      │                  │
     └──────────────────────────────────────┴── US6 (Dashboard)│
                                                               │
Foundation (Auth) ─────────────────────────────────────────────┘
```

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:

- **Phase 1**: T004-T010 (project init files)
- **Phase 2**: T016-T017 (models)
- **Phase 3**: T029-T030 (sample content)
- **Phase 4**: T043-T044, T048-T049 (models, API)
- **Phase 5**: None (linear)
- **Phase 6**: T084-T085, T090-T093 (models, components)
- **Phase 9**: T098-T105 (polish tasks)

---

## Parallel Example: User Story 4

```bash
# Launch model creation in parallel:
Task: T065 "Create Quiz model in backend/src/models/quiz.py"
Task: T066 "Create Question model in backend/src/models/quiz.py"
Task: T067 "Create QuizAttempt model in backend/src/models/quiz.py"

# After models complete, launch components in parallel:
Task: T073 "Create Quiz component"
Task: T074 "Create QuizQuestion component"
Task: T075 "Create QuizResults component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Browse Textbook)
4. **STOP and VALIDATE**: Test browsing, navigation, typography
5. Deploy demo if ready

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready
2. Add US1 (Browse) → Test → Demo (MVP!)
3. Add US2 (RAG) → Test → Demo (Interactive Q&A!)
4. Add US3 (Urdu) → Test → Demo (Bilingual!)
5. Add US4 (Quiz) → Test → Demo (Assessment!)
6. Add US5 (Summary) → Test → Demo (Enhanced!)
7. Add US6 (Dashboard) → Test → Demo (Personalized!)
8. Phase 9 → Polish → Final submission

### Hackathon Priority

For hackathon demo, prioritize:
1. ✅ US1: Browsable textbook (core requirement)
2. ✅ US2: RAG chatbot with citations (AI feature)
3. ✅ US3: Urdu translation (bonus feature)
4. ✅ US4: Quizzes (bonus feature)
5. ✅ US6: Dashboard (personalization bonus)
6. ⚡ Polish: Demo video, deployment

---

## Task Summary

| Phase | Tasks | Parallel Tasks | Description |
|-------|-------|----------------|-------------|
| 1. Setup | 10 | 7 | Project initialization |
| 2. Foundational | 17 | 2 | Auth, database, core services |
| 3. US1 Browse | 11 | 2 | Textbook content and navigation |
| 4. US2 RAG | 15 | 3 | Chatbot with citations |
| 5. US3 Urdu | 11 | 0 | Translation and RTL |
| 6. US4 Quiz | 13 | 4 | Quiz generation and taking |
| 7. US5 Summary | 6 | 0 | Chapter summaries |
| 8. US6 Dashboard | 13 | 5 | Personalization |
| 9. Polish | 11 | 5 | Accessibility, deployment |
| **Total** | **107** | **28** | |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Authentication (US7 in spec) is in Foundational phase since it's required for US6
