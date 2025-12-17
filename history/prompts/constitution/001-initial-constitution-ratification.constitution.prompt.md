---
id: 001
title: Initial Constitution Ratification
stage: constitution
date: 2025-12-17
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: Shaista Tosif
command: /sp.constitution
labels: ["constitution", "governance", "initialization", "hackathon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

```text
author:
  name: Shaista Tosif
  email: shaistatosif34@gmail.com
  linkedin: https://www.linkedin.com/in/shaista-tosif-43757a2b6
  location: Karachi, Pakistan

purpose: |
  Defines rules, workflow, structure, quality standards, and
  constraints for producing a complete AI-native robotics textbook,
  RAG system, Urdu translation, and personalized dashboard.

guiding_principles:
  - Deterministic, structured, and testable outputs.
  - No hallucinations or unstated assumptions.
  - Requirements → Tasks → Implementations must always align.
  - Maintain academic clarity & professional textbook design.
  - Modular multi-agent architecture.
  - RAG answers must be accurate with citations.
  - Urdu translation must preserve meaning and formatting.
  - All components must satisfy hackathon scoring.

definitions:
  ai_native_book: "A Docusaurus textbook enhanced with AI assistance, RAG, personalization, and translation."
  rag_system: "Chunking + embeddings + Qdrant search + Gemini answer generation."
  agent: "An AI actor responsible for a specific function."
  subagent: "Claude Code micro-agent for file editing and code generation."
  specification: "Complete, measurable, tech-agnostic requirement document."
  done_definition: "Fully functional, validated, and ambiguity-free output."
  mcp_server: "An external context provider implementing the Model Context Protocol."
  github_mcp: "An MCP server enabling structured interaction with the GitHub repository."
  context7: "An MCP server supplying authoritative framework documentation."

workflow:
  - "/sp.constitution": Defines rules and system governance.
  - "/sp.specify": Generates full functional specification.
  - "/sp.plan": Produces architecture & system diagrams.
  - "/sp.tasks": Breaks plan into concrete tasks.
  - "/sp.implement": Creates final code via Claude Code + subagents.

quality_standards:
  specifications:
    - Must define user stories, edge cases, and success criteria.
  plans:
    - Must include diagrams, agent boundaries, and data flow.
  tasks:
    - Each task outputs a file or behavior.
    - ≤ 200 tasks.
  implementations:
    - Must follow clean architecture and avoid unused files.

constraints:
  general:
    - No hallucinations.
    - No mixing of phases.

  frontend:
    - Must use Docusaurus.
    - Must support Urdu RTL.
    - Must maintain professional typography and accessibility (WCAG AA).

  backend:
    - FastAPI + Gemini 2.5 Flash + Qdrant Cloud.
    - Must support concurrent users and low-latency responses.

  rag:
    - Must include citations.
    - Must avoid cutting sentences during chunking.
    - Must respond with limitations if query is outside textbook scope.

  translation:
    - Maintain tone and semantic meaning.
    - Do not translate code blocks.
    - Apply RTL layout only in Urdu mode.

  personalization:
    - Based on user metadata.
    - Must not alter factual correctness.

  agents:
    - Each agent must have a narrow, isolated responsibility.
    - No cross-contamination of responsibilities.

mcp_infrastructure:
  enabled: true
  servers:
    github:
      type: mcp
      purpose: Enables autonomous interaction with the GitHub repository
      capabilities:
        - Read repository files
        - Modify and commit files
        - Analyze project structure
        - Validate README, docs, and code consistency
      constraints:
        - No destructive operations
        - Preserve clean architecture
        - Commits must be logically grouped

    context7:
      type: mcp
      purpose: Provides authoritative, up-to-date documentation for frameworks
      capabilities:
        - Fetch official API references
        - Validate syntax and best practices
        - Reduce hallucinations in generated code
      constraints:
        - Prefer official sources only
        - Must not override project specifications

  usage_policy:
    - MCP servers are optional but preferred.
    - Agents must fall back to internal knowledge if MCP is unavailable.
    - MCP context must never contradict sp.specify requirements.

agents:
  planner_agent:
    responsibility: Architecture planning and system decomposition.
  ui_agent:
    responsibility: UI/UX generation and Docusaurus integration.
  code_agent:
    responsibility: Backend, frontend, and integration code generation.
  file_agent:
    responsibility: File creation, modification, and repository hygiene.
  mcp_orchestrator:
    responsibility: Coordinates access to MCP servers, validates external context

acceptance_criteria:
  - All hackathon requirements met.
  - All bonus features included:
      * Subagents
      * Personalization
      * Urdu translation
      * BetterAuth
      * RAG chatbot
      * Quizzes & summaries
      * Dashboard
      * MCP servers (GitHub + Context7)
  - Clean repository structure.
  - Working deployment.
  - Demo video under 90 seconds.
```

## Response snapshot

Created initial constitution v1.0.0 for AI-Native Humanoid Robotics Textbook project.

Key deliverables:
- 8 core principles mapped from guiding_principles (Deterministic Outputs, No Hallucinations, Traceability, Academic Clarity, Modular Architecture, RAG Accuracy, Translation Fidelity, Hackathon Compliance)
- Technical constraints section covering frontend (Docusaurus, RTL, WCAG AA), backend (FastAPI, Gemini, Qdrant), RAG, personalization, and security
- Development workflow documenting 5-phase SDD process
- MCP Infrastructure section for GitHub and Context7 servers
- Governance section with amendment process and semantic versioning
- Acceptance criteria checklist for hackathon completion

All placeholders replaced. Sync Impact Report embedded as HTML comment. Templates validated as compatible.

## Outcome

- Impact: Initial project constitution ratified, establishing governance for hackathon submission
- Tests: N/A (governance document)
- Files: .specify/memory/constitution.md created
- Next prompts: `/sp.specify` to generate feature specification
- Reflection: User provided comprehensive YAML input with clear structure; mapped 8 guiding principles to constitution principles with rationale

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS - all placeholders filled, no TODO markers remaining
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - initial constitution complete
