.PHONY: setup-backend setup-frontend migrate seed backend frontend test-backend test-frontend

setup-backend:
	cd backend && python -m venv .venv && . .venv/Scripts/activate && pip install -e .[dev]

setup-frontend:
	cd frontend && npm install

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.seed.seed

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test-backend:
	cd backend && pytest -q

test-frontend:
	cd frontend && npm test
