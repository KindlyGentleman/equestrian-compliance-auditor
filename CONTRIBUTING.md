# Contributing to Maison Équestre Atelier Pro

Thank you for contributing to the **Equestrian Compliance & Specification Auditor**. This document outlines development standards, branch conventions, and testing workflows to ensure the repository remains robust and production-ready.

---

## 1. Development Prerequisites

- **Python**: `>= 3.11` (Python 3.12 recommended)
- **Node.js**: `>= 20.x` (Node 22 LTS recommended) with `npm`
- **Docker & Docker Compose**: Optional for containerized local workflows

---

## 2. Local Environment Setup

### Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install core and dev dependencies
pip install -e ".[dev]"

# Copy and configure environment variables
cp .env.example .env
```

### Frontend Setup
```bash
cd frontend
npm install
```

---

## 3. Running Services Locally

### Backend Server
```bash
# Starts FastAPI server at http://127.0.0.1:8000 (docs at /docs)
make dev-backend
# Or directly:
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Development Server
```bash
# Starts Next.js 14 at http://localhost:3000
make dev-frontend
# Or directly:
cd frontend && npm run dev
```

### Full-Stack with Docker Compose
```bash
make docker-up
# Verify health
curl http://localhost:8000/api/health
```

---

## 4. Code Standards & Antislop Principles

All code, comments, and documentation must adhere to professional engineering hygiene:

1. **No Generic AI Slop**:
   - Avoid decorative comment banners (`# ====== SECTION ===== #`).
   - Do not narrate obvious code step-by-step.
   - Do not use em-dashes in code comments or user-facing copy.
2. **Quiet Luxury Palette & Typography**:
   - The UI follows a bespoke equestrian palette: deep forest green (`#163828`), luxury slate (`#151C22`), warm parchment (`#FBFBF9`), and subtle brass (`#9E7E50`).
   - Avoid generic blue-purple gradients, aggressive drop shadows, or unstyled system fonts.
3. **Type Safety**:
   - Backend: All models and signatures must use Pydantic v2 schemas and standard Python type hints.
   - Frontend: Strict TypeScript mode with zero `any` shortcuts where interfaces exist in `src/types/index.ts`.

---

## 5. Testing & Quality Assurance

Run the automated test suite before opening any pull request:

```bash
# Run full backend test suite (54+ tests)
make test

# Run stakeholder demonstration benchmark test (<90s SLA)
make test-demo

# Run linter
make lint

# Verify frontend production build
make build-frontend
```

---

## 6. Commit Message Convention

Follow standard Conventional Commits:
- `feat(engine)`: New compliance check or scoring logic
- `feat(api)`: New FastAPI endpoint or router update
- `feat(ui)`: New frontend component or screen
- `fix(rag)`: Bug fix in document chunking or vector search
- `docs`: Documentation improvements
- `refactor`: Structural codebase improvements without behavior change
- `test`: Test suite additions or fixture updates
