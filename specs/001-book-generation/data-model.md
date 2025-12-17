# Data Model: Book Generation

**Feature**: 001-book-generation
**Date**: 2025-12-17
**Status**: Complete

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│     User        │       │    Chapter      │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ email           │       │ title           │
│ password_hash   │       │ slug            │
│ display_name    │       │ order           │
│ language_pref   │       │ description     │
│ created_at      │       │ summary         │
│ updated_at      │       │ content_path    │
│ is_verified     │       │ urdu_path       │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │ 1:N                     │ 1:N
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│ ReadingProgress │       │     Quiz        │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ chapter_id (FK) │
│ chapter_id      │       │ title           │
│ section_id      │       │ created_at      │
│ completed       │       └────────┬────────┘
│ time_spent_sec  │                │
│ last_accessed   │                │ 1:N
└─────────────────┘                ▼
                          ┌─────────────────┐
┌─────────────────┐       │   Question      │
│    Bookmark     │       ├─────────────────┤
├─────────────────┤       │ id (PK)         │
│ id (PK)         │       │ quiz_id (FK)    │
│ user_id (FK)    │       │ question_text   │
│ chapter_id      │       │ question_type   │
│ section_id      │       │ options (JSON)  │
│ created_at      │       │ correct_answer  │
└─────────────────┘       │ order           │
                          └─────────────────┘
┌─────────────────┐
│  QuizAttempt    │       ┌─────────────────┐
├─────────────────┤       │  ChatSession    │
│ id (PK)         │       ├─────────────────┤
│ user_id (FK)    │       │ id (PK)         │
│ quiz_id (FK)    │       │ user_id (FK)    │
│ score           │       │ created_at      │
│ total_questions │       │ updated_at      │
│ answers (JSON)  │       └────────┬────────┘
│ started_at      │                │
│ completed_at    │                │ 1:N
└─────────────────┘                ▼
                          ┌─────────────────┐
                          │  ChatMessage    │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ session_id (FK) │
                          │ role            │
                          │ content         │
                          │ citations (JSON)│
                          │ created_at      │
                          └─────────────────┘
```

## Entity Definitions

### User

Represents a registered learner on the platform.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| email | String(255) | UNIQUE, NOT NULL | Login email address |
| password_hash | String(255) | NOT NULL | Bcrypt hashed password |
| display_name | String(100) | NULL | Optional display name |
| language_pref | Enum('en', 'ur') | DEFAULT 'en' | Preferred language |
| created_at | DateTime | NOT NULL, auto | Account creation timestamp |
| updated_at | DateTime | NOT NULL, auto | Last update timestamp |
| is_verified | Boolean | DEFAULT false | Email verification status |

**Validation Rules**:
- Email must be valid format
- Password must be >= 8 characters before hashing
- Display name max 100 characters

---

### Chapter

Represents a major section of the textbook.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String(50) | PK | Slug-based ID (e.g., "chapter-1") |
| title | String(200) | NOT NULL | Chapter title |
| slug | String(100) | UNIQUE, NOT NULL | URL-friendly identifier |
| order | Integer | NOT NULL | Display order (1, 2, 3...) |
| description | Text | NULL | Brief chapter description |
| summary | Text | NULL | AI-generated summary |
| content_path | String(500) | NOT NULL | Path to English markdown |
| urdu_path | String(500) | NULL | Path to Urdu markdown |

**Validation Rules**:
- Order must be positive integer
- Slug must be URL-safe (lowercase, hyphens only)
- Content path must exist in filesystem

---

### ReadingProgress

Tracks user progress through textbook content.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → User.id, NOT NULL | Reference to user |
| chapter_id | String(50) | NOT NULL | Reference to chapter |
| section_id | String(100) | NULL | Specific section within chapter |
| completed | Boolean | DEFAULT false | Whether user finished this section |
| time_spent_sec | Integer | DEFAULT 0 | Cumulative time spent reading |
| last_accessed | DateTime | NOT NULL, auto | Last access timestamp |

**Validation Rules**:
- Unique constraint on (user_id, chapter_id, section_id)
- time_spent_sec must be >= 0

---

### Bookmark

User-saved locations in the textbook.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → User.id, NOT NULL | Reference to user |
| chapter_id | String(50) | NOT NULL | Reference to chapter |
| section_id | String(100) | NULL | Specific section (optional) |
| created_at | DateTime | NOT NULL, auto | When bookmark was created |

**Validation Rules**:
- Unique constraint on (user_id, chapter_id, section_id)

---

### Quiz

A set of questions for a chapter.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| chapter_id | String(50) | FK → Chapter.id, NOT NULL | Associated chapter |
| title | String(200) | NOT NULL | Quiz title |
| created_at | DateTime | NOT NULL, auto | When quiz was generated |

**Validation Rules**:
- One quiz per chapter (unique constraint on chapter_id)

---

### Question

Individual question within a quiz.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| quiz_id | UUID | FK → Quiz.id, NOT NULL | Parent quiz |
| question_text | Text | NOT NULL | The question content |
| question_type | Enum('multiple_choice', 'short_answer') | NOT NULL | Question format |
| options | JSON | NULL | Array of options for MCQ |
| correct_answer | Text | NOT NULL | Correct answer text |
| order | Integer | NOT NULL | Display order within quiz |

**Validation Rules**:
- If type is 'multiple_choice', options must have 3-5 items
- Order must be positive integer
- correct_answer must match one of the options for MCQ

**Options JSON Schema** (for multiple_choice):
```json
{
  "options": ["Option A", "Option B", "Option C", "Option D"]
}
```

---

### QuizAttempt

Records a user's attempt at a quiz.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → User.id, NOT NULL | Reference to user |
| quiz_id | UUID | FK → Quiz.id, NOT NULL | Reference to quiz |
| score | Integer | NOT NULL | Number of correct answers |
| total_questions | Integer | NOT NULL | Total questions in quiz |
| answers | JSON | NOT NULL | User's answers |
| started_at | DateTime | NOT NULL | When attempt began |
| completed_at | DateTime | NULL | When attempt finished |

**Validation Rules**:
- Score must be 0 <= score <= total_questions
- completed_at must be >= started_at if not null

**Answers JSON Schema**:
```json
{
  "answers": [
    {"question_id": "uuid", "answer": "User's answer"},
    {"question_id": "uuid", "answer": "User's answer"}
  ]
}
```

---

### ChatSession

A conversation session with the RAG chatbot.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → User.id, NULL | Reference to user (null for anonymous) |
| created_at | DateTime | NOT NULL, auto | Session start time |
| updated_at | DateTime | NOT NULL, auto | Last message time |

---

### ChatMessage

Individual message in a chat session.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| session_id | UUID | FK → ChatSession.id, NOT NULL | Parent session |
| role | Enum('user', 'assistant') | NOT NULL | Message sender |
| content | Text | NOT NULL | Message content |
| citations | JSON | NULL | Source citations for assistant messages |
| created_at | DateTime | NOT NULL, auto | Message timestamp |

**Citations JSON Schema**:
```json
{
  "citations": [
    {"chapter_id": "chapter-1", "section": "Introduction", "text": "Relevant quote..."},
    {"chapter_id": "chapter-2", "section": "Components", "text": "Another quote..."}
  ]
}
```

---

## Vector Store Schema (Qdrant)

### Collection: `textbook_chunks`

Stores embedded chunks of textbook content for RAG retrieval.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique chunk identifier |
| vector | Float[768] | Gemini embedding vector |
| chapter_id | String | Source chapter ID |
| section_id | String | Source section ID |
| chunk_text | String | Original text content |
| chunk_order | Integer | Order within section |
| language | String | 'en' or 'ur' |

**Metadata Payload**:
```json
{
  "chapter_id": "chapter-1",
  "section_id": "introduction",
  "chunk_text": "Humanoid robots are machines designed to...",
  "chunk_order": 1,
  "language": "en",
  "title": "Introduction to Humanoid Robotics"
}
```

---

## State Transitions

### User Verification State

```
[Created] → [Verification Email Sent] → [Verified]
                     ↓
              [Expired/Invalid]
```

### Quiz Attempt State

```
[Started] → [In Progress] → [Completed]
               ↓
          [Abandoned] (if session expires)
```

### Reading Progress State

```
[Not Started] → [In Progress] → [Completed]
                    ↑________________|
                   (can revisit)
```

---

## Indexes

### Performance Indexes

| Table | Columns | Type | Purpose |
|-------|---------|------|---------|
| User | email | UNIQUE | Fast login lookup |
| ReadingProgress | (user_id, chapter_id) | COMPOSITE | Progress queries |
| Bookmark | (user_id) | INDEX | User bookmark listing |
| QuizAttempt | (user_id, quiz_id) | COMPOSITE | User quiz history |
| ChatMessage | (session_id, created_at) | COMPOSITE | Message ordering |

### Qdrant Indexes

- Vector index on embedding dimension (automatic)
- Payload filter indexes on: chapter_id, language
