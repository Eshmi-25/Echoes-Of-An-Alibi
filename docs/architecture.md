# Architecture

Echoes of the Alibi uses a split frontend/backend monorepo.

- Frontend: Next.js App Router with TypeScript, TanStack Query, Zustand, React Hook Form, Zod.
- Backend: FastAPI + SQLAlchemy 2 + Pydantic 2 + Alembic.
- AI: Ollama local model through HTTPX with deterministic fallback templates.
- Data ownership: Canonical case solution is backend-only and never exposed pre-resolution.

## High-level Components

- Client routes for game views and interaction.
- API service layer with normalized errors.
- Auth with JWT bearer tokens.
- Deterministic game engine for unlocks, contradictions, scoring.
- Dialogue service that constrains LLM output to JSON schema.
- SQLite default database with switchable DATABASE_URL.

## Security Notes

- Generic auth errors.
- Ownership checks on all investigation routes.
- Input limits for chat messages.
- Pydantic validation for all LLM responses.
- In-memory interview rate limiter (development-oriented).
