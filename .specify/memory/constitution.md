<!--
SYNC IMPACT REPORT
==================
Version change: N/A (initial) → 1.0.0
Modified principles: N/A (initial ratification)
Added sections:
  - Core Principles (8 principles)
  - Technical Constraints
  - Development Workflow
  - Agent Governance
  - MCP Infrastructure
  - Governance
Removed sections: None (initial document)
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (user stories structure aligns)
  - .specify/templates/tasks-template.md: ✅ Compatible (phase structure supports workflow)
Follow-up TODOs: None
-->

# AI-Native Humanoid Robotics Textbook Constitution

**Author**: Shaista Tosif
**Contact**: shaistatosif34@gmail.com
**LinkedIn**: https://www.linkedin.com/in/shaista-tosif-43757a2b6
**Location**: Karachi, Pakistan

## Purpose

This constitution defines the rules, workflow, structure, quality standards, and constraints
for producing a complete AI-native robotics textbook with RAG system, Urdu translation,
and personalized dashboard for hackathon submission.

## Core Principles

### I. Deterministic Outputs

All system outputs MUST be deterministic, structured, and testable. No component may
produce non-reproducible results under identical inputs. Every artifact generated
by agents MUST follow a defined schema and validation process.

**Rationale**: Reproducibility enables debugging, testing, and academic credibility.

### II. No Hallucinations

Agents MUST NOT generate hallucinated content, unstated assumptions, or invented data.
All claims MUST be grounded in source material (textbook content) or explicitly marked
as limitations. RAG responses MUST include citations to source chunks.

**Rationale**: Academic integrity and user trust require factual accuracy.

### III. Traceability

Requirements → Tasks → Implementations MUST always align. Every implementation task
MUST trace back to a specification requirement. Every deployed feature MUST have a
corresponding task and spec entry. PHRs (Prompt History Records) MUST document all
significant AI interactions.

**Rationale**: Audit trail ensures accountability and enables debugging of scope drift.

### IV. Academic Clarity

All textbook content MUST maintain academic clarity and professional design standards.
Typography MUST follow established textbook conventions. Diagrams MUST be clear and
labeled. Code examples MUST be syntactically correct and runnable where applicable.

**Rationale**: Educational materials require professional presentation for credibility.

### V. Modular Architecture

The system MUST use a modular multi-agent architecture where each agent has a narrow,
isolated responsibility. No cross-contamination of responsibilities between agents.
Components MUST be independently testable and replaceable.

**Agents**:
- **planner_agent**: Architecture planning and system decomposition
- **ui_agent**: UI/UX generation and Docusaurus integration
- **code_agent**: Backend, frontend, and integration code generation
- **file_agent**: File creation, modification, and repository hygiene
- **mcp_orchestrator**: MCP server coordination and context validation

### VI. RAG Accuracy

RAG (Retrieval-Augmented Generation) answers MUST be accurate with citations. Chunking
MUST NOT cut sentences mid-thought. Responses MUST acknowledge limitations when queries
fall outside textbook scope. Citation format MUST include chapter/section references.

**Rationale**: Incorrect answers undermine the educational purpose of the system.

### VII. Translation Fidelity

Urdu translation MUST preserve semantic meaning, tone, and academic register. Code
blocks MUST NOT be translated. RTL (Right-to-Left) layout MUST be applied only in
Urdu mode. Technical terms MAY retain English with Urdu transliteration in parentheses.

**Rationale**: Translation must serve Urdu-speaking learners without introducing errors.

### VIII. Hackathon Compliance

All components MUST satisfy hackathon scoring criteria. Bonus features (subagents,
personalization, Urdu translation, BetterAuth, RAG chatbot, quizzes, summaries,
dashboard, MCP servers) MUST be implemented. Demo video MUST be under 90 seconds.

**Rationale**: Project success is measured against hackathon evaluation rubric.

## Technical Constraints

### Frontend

- MUST use Docusaurus for textbook presentation
- MUST support Urdu RTL layout
- MUST maintain professional typography
- MUST meet WCAG AA accessibility standards
- MUST be responsive for desktop and tablet

### Backend

- MUST use FastAPI for API layer
- MUST use Gemini 2.5 Flash for LLM operations
- MUST use Qdrant Cloud for vector storage
- MUST support concurrent users
- MUST achieve low-latency responses (< 2s for RAG queries)

### RAG System

- Chunking MUST NOT split sentences
- All responses MUST include source citations
- Out-of-scope queries MUST return acknowledgment of limitations
- Embeddings MUST be generated consistently

### Personalization

- Personalization MUST be based on user metadata
- Personalized content MUST NOT alter factual correctness
- User preferences MUST be stored securely

### Security

- No hardcoded secrets or tokens
- All secrets via environment variables
- Authentication via BetterAuth
- Secure data handling for user information

## Development Workflow

The project follows a five-phase specification-driven workflow:

1. **`/sp.constitution`**: Defines rules and system governance (this document)
2. **`/sp.specify`**: Generates full functional specification
3. **`/sp.plan`**: Produces architecture and system diagrams
4. **`/sp.tasks`**: Breaks plan into concrete, executable tasks
5. **`/sp.implement`**: Creates final code via Claude Code + subagents

### Quality Gates

**Specifications**:
- MUST define user stories with acceptance criteria
- MUST identify edge cases
- MUST include success criteria

**Plans**:
- MUST include system diagrams
- MUST define agent boundaries
- MUST document data flow

**Tasks**:
- Each task MUST output a file or observable behavior
- Maximum 200 tasks per feature
- Tasks MUST be independently completable

**Implementations**:
- MUST follow clean architecture
- MUST NOT include unused files
- MUST pass all defined tests

## MCP Infrastructure

Model Context Protocol (MCP) servers provide structured, real-time access to external
systems, repositories, and documentation sources.

### GitHub MCP Server

**Purpose**: Autonomous interaction with the GitHub repository for code inspection,
documentation alignment, and non-destructive updates.

**Capabilities**:
- Read repository files
- Modify and commit files
- Analyze project structure
- Validate README and docs consistency

**Constraints**:
- No destructive operations
- Preserve clean architecture
- Commits MUST be logically grouped

### Context7 MCP Server

**Purpose**: Authoritative, up-to-date documentation for frameworks, SDKs, and
libraries used in the project.

**Capabilities**:
- Fetch official API references
- Validate syntax and best practices
- Reduce hallucinations in generated code

**Constraints**:
- Prefer official sources only
- MUST NOT override project specifications

### Usage Policy

- MCP servers are preferred but optional
- Agents MUST fall back to internal knowledge if MCP unavailable
- MCP context MUST NOT contradict `/sp.specify` requirements

## Governance

### Amendment Process

1. Proposed amendments MUST be documented with rationale
2. Amendments MUST include migration plan for affected artifacts
3. Version MUST be incremented per semantic versioning:
   - **MAJOR**: Backward-incompatible governance/principle changes
   - **MINOR**: New principles or materially expanded guidance
   - **PATCH**: Clarifications, wording, non-semantic refinements

### Compliance

- All PRs MUST verify compliance with this constitution
- Complexity beyond constitution allowances MUST be justified
- Use CLAUDE.md for runtime development guidance

### Definitions

| Term | Definition |
|------|------------|
| ai_native_book | Docusaurus textbook with AI assistance, RAG, personalization, translation |
| rag_system | Chunking + embeddings + Qdrant search + Gemini answer generation |
| agent | AI actor responsible for a specific function |
| subagent | Claude Code micro-agent for file editing and code generation |
| specification | Complete, measurable, tech-agnostic requirement document |
| done_definition | Fully functional, validated, and ambiguity-free output |
| mcp_server | External context provider implementing Model Context Protocol |

## Acceptance Criteria

This project is considered complete when:

- [ ] All hackathon requirements met
- [ ] Subagents implemented and functional
- [ ] Personalization based on user metadata
- [ ] Urdu translation with RTL support
- [ ] BetterAuth integration complete
- [ ] RAG chatbot with citations
- [ ] Quizzes and summaries generated
- [ ] Dashboard functional
- [ ] MCP servers (GitHub + Context7) integrated
- [ ] Clean repository structure
- [ ] Working deployment
- [ ] Demo video under 90 seconds

**Version**: 1.0.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-17
