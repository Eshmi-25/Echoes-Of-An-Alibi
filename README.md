# ECHOES OF AN ALIBI

Tagline: Every suspect remembers the night differently.

## 1. Purpose

Echoes of the Alibi is a full-stack AI-assisted detective game where players investigate a fictional case, interrogate suspects, connect evidence, expose contradictions, and submit a final accusation scored by a deterministic backend game engine.

This project uses fictional characters and events.
The LLM performs constrained character dialogue.
The backend owns the authoritative case state and solution.
Ollama is optional because deterministic fallback dialogue is included.

## 2. Main Gameplay Features

- One complete case: The Midnight Gallery
- 5 suspects with unique personalities, motives, and timelines
- 5 explorable locations with unlock rules
- 13 clues, 5 contradictions, 3 red herrings
- Action-limited investigation loop
- AI interrogation with strict JSON schema
- React Flow evidence board with save/load
- Detective notes, timeline review, final accusation, and multiple endings

## 3. Tech Stack

### Frontend
- Next.js App Router
- TypeScript
- Tailwind CSS
- Zustand
- TanStack Query
- React Hook Form + Zod
- Lucide React
- Framer Motion
- React Flow
- Axios

### Backend
- FastAPI
- SQLAlchemy 2.x
- Pydantic 2
- Alembic
- JWT auth (python-jose)
- Passlib + bcrypt
- HTTPX (Ollama integration)

### Database
- SQLite by default
- Configurable DATABASE_URL for PostgreSQL later

### AI
- Local Ollama model via environment variables
- Deterministic fallback mode when Ollama is unavailable

### Testing
- Pytest (backend)
- Vitest (frontend)

### Tooling
- Docker + Docker Compose
- GitHub Actions CI
- Ruff + ESLint + TypeScript strict mode

## 4. Architecture Overview

Frontend consumes authenticated backend REST endpoints.
Backend enforces game rules, security checks, and authoritative state transitions.
LLM responses are validated and sanitized, but never trusted for scoring/unlocks.

## 5. System Architecture Diagram

```mermaid
flowchart LR
	Player[Player Browser] --> FE[Next.js Frontend]
	FE --> API[FastAPI Backend]
	API --> DB[(SQLite / PostgreSQL)]
	API --> GE[Deterministic Game Engine]
	API --> DS[Dialogue Service]
	DS --> AI{Ollama Enabled?}
	AI -->|Yes| OLLAMA[Local Ollama]
	AI -->|No/Fail| FALLBACK[Template Fallback Dialogue]
	GE --> SCORE[Scoring + Endings]
```

## 6. Game Flow Diagram

```mermaid
flowchart TD
	A[Register / Login] --> B[Start Investigation]
	B --> C[Read Briefing]
	C --> D[Search Locations]
	D --> E[Unlock Clues / Suspects / Topics]
	E --> F[Interrogate Suspects]
	F --> G[Expose Contradictions]
	G --> H[Update Notes + Evidence Board]
	H --> I[Submit Final Accusation]
	I --> J[Backend Scores Deterministically]
	J --> K[Ending + Case Review]
```

## 7. Repository Structure

See the monorepo tree under:
- frontend/
- backend/
- docs/

## 8. Prerequisites

- Node.js 20+
- Python 3.11+
- pip
- Docker Desktop (optional)
- Ollama (optional)


## 9. Test Commands

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm test
```

## 10. API Documentation

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 11. Default Development URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## 12. Security Considerations

- JWT auth with hashed passwords
- Generic auth errors
- Investigation ownership checks
- Message length limits
- LLM output validation and sanitization
- Prompt-constrained dialogue actor model
- In-memory rate limiting for interviews (development-only)

For scaled deployment, replace in-memory rate limiting with shared infrastructure (Redis or equivalent).

## 13. Known Limitations

- Rate limiting is process-local and non-distributed
- Token storage uses localStorage in MVP client
- Frontend test suite is compact and can be expanded with more interaction tests


## 14. Troubleshooting

- 401 errors: verify token exists and backend secret is consistent.
- No AI response: check Ollama service, model name, or set OLLAMA_ENABLED=false.
- Empty case list: run seed command.
- CORS issues: verify CORS_ORIGINS includes frontend host.


## 15. License

MIT License. See LICENSE.

