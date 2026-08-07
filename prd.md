# Lumina — PRD: Project Structure & File Map

## Overview

Lumina is a clinical decision-support platform for rare disease triage. It ingests multimodal clinical evidence (notes, images, lab reports, genetic VCFs), extracts Human Phenotype Ontology (HPO) terms, scores candidate diseases using ontology similarity metrics, and generates doctor-reviewed referral letters. The platform follows a **Doctor-in-the-Loop** principle: AI extracts and suggests, but clinicians accept/reject each phenotype before scoring.

**Architecture**: Next.js 16 frontend (web app) + FastAPI backend (Python) + local SQLite databases.

---

## Repository Structure

```
lumina/
├── apps/
│   ├── api/                  # FastAPI backend service
│   │   ├── main.py           # FastAPI app: lifespan, middleware, route registration, health check
│   │   ├── .env.local        # Clerk publishable key + secret key (NEXT_PUBLIC_*)
│   │   ├── .env               # Backend env vars: GROQ_API_KEY, DATABASE_URL, CORS, etc.
│   │   ├── app_db.py          # SQLite engine resolution and schema init
│   │   ├── app_models.py      # SQLModel tables: PatientSubmission, DoctorRequestMessage, ClinicalCase
│   │   ├── routes/            # API route modules
│   │   │   ├── __init__.py
│   │   │   ├── agent.py       # Agent loop: next question, letter generation, patient summary
│   │   │   ├── disease.py     # Disease lookup & scoring
│   │   │   ├── fhir.py         # FHIR export
│   │   │   ├── intake.py       # Multimodal intake endpoints: text, photo, lab, vcf
│   │   │   ├── score.py        # HPO differential scoring
│   │   │   ├── search.py       # Semantic HPO search via embeddings
│   │   │   ├── submissions.py  # Patient submission CRUD + doctor review workflow
│   │   │   └── __pycache__/
│   │   ├── api/               # Core application logic
│   │   │   ├── __init__.py
│   │   │   └── app_models.py  # SQLModel model definitions
│   │   ├── tests/             # API tests
│   │   └── .venv/             # Python virtual environment
│   │       └── ...
│   ├── web/                  # Next.js 16 frontend
│   │   ├── src/
│   │   │   ├── lib/           # Utility modules
│   │   │   │   ├── api.ts           # API client functions (fetch wrapper)
│   │   │   │   ├── clerk-localization.ts  # Clerk i18n
│   │   │   │   ├── user-role.ts     # User role resolution
│   │   │   │   ├── formatters.ts     # Formatting helpers
│   │   │   │   ├── utils.ts           # General utilities
│   │   │   │   ├── hpo.ts             # HPO term helpers
│   │   │   │   ├── demo-cases.ts      # Demo data
│   │   │   ├── i18n/               # Internationalization
│   │   │   │   └── routing.ts       # next-intl routing config
│   │   │   └── components/         # React components
│   │   │       ├── lumina/
│   │   │       │   ├── role-guard.tsx   # Role-based access control
│   │   │       │   ├── product-page.tsx  # Product display
│   │   │       │   ├── info-page.tsx     # Information display
│   │   │       │   ├── referral-letter-sheet.tsx
│   │   │       └── ...
│   │   ├── package.json        # Frontend dependencies (Next.js, @clerk, etc.)
│   │   └── .env.local          # Clerk keys + NEXT_PUBLIC_API_URL (separate from API .env.local)
│   └── .vite.env              # Vite env config
│   └── vercel.json             # Vercel config
│   └── .gitignore
│
├── packages/
│   ├── agent/                  # Referral letter generation & agent loop
│   │   ├── src/
│   │   │   └── ...
│   │   └── .venv/
│   ├── extractors/             # Multimodal extraction (notes, photo, lab, VCF)
│   │   ├── lab.py               # Lab report extraction
│   │   ├── notes.py             # Clinical note extraction
│   │   ├── photo.py             # Photo extraction
│   │   ├── validate.py          # Validation helpers
│   │   └── vcf.py               # VCF parsing
│   ├── ingest/                  # Knowledge graph models (HPO, Orphanet, ClinVar, FGDD)
│   │   ├── models.py
│   │   └── ...
│   ├── schemas/                # Shared TypeScript schemas
│   │   ├── index.ts
│   │   ├── disease.ts
│   │   ├── case.ts
│   │   └── hpo.ts
│   └── scoring/                # HPO similarity ranker & scoring engine
│       └── ...
│
├── database/
│   ├── orpha.sqlite             # Knowledge graph (read-only, git LFS-tracked)
│   └── lumina_app.sqlite       # Runtime app DB (submissions, cases, messages)
│
├── scripts/
│   ├── build_hpo_index.py      # Build HPO embedding index (sentence-transformers)
│   ├── eval.py                 # Evaluation utilities
│   └── train_xgb.py            # XGBoost training
│
├── tests/
│   ├── test_api.py              # API endpoint tests
│   ├── test_ingest.py           # Ingestion pipeline tests
│   └── test_scoring.py          # Scoring logic tests
│
├── .env                        # Backend env (GROQ_API_KEY, DATABASE_URL, etc.)
├── .env.local                  # Frontend env (NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY)
├── .env.example                # Example env file with placeholders
├── README.md                    # Project overview & setup guide
├── package.json                # Root monorepo config (pnpm)
├── vercel.json                 # Vercel deployment config
├── .github/
│   └── workflows/
│       └── ci.yml              # CI pipeline
├── supabase_migration.sql      # Supabase migration
└── .claude/
│   └── settings.*.json         # Claude settings
│
└── docs/
    └── assets/
        └── referral-letter-example.pdf
```

---

## File Descriptions

### Backend (`apps/api/`)

| File | Purpose |
|------|---------|
| **main.py** | FastAPI application entry point. Sets up lifespan (DB init, scoring index load, vocab loading), CORS middleware, and registers all route modules. |
| **app_db.py** | Database engine resolution. Detects PostgreSQL (Supabase) vs SQLite, resolves the `LUMINA_APP_DATABASE_URL` env var, and creates/initializes the SQLite app database with column migrations. |
| **app_models.py** | SQLModel data models: `PatientSubmission`, `DoctorRequestMessage`, `ClinicalCase`. Define all tables and their relationships. |
| **routes/intake.py** | Multimodal intake endpoints (`/intake/text`, `/intake/photo`, `/intake/lab`, `/intake/vcf`). Extracts HPO terms from clinical notes, photos, lab reports, and VCF files. Validates terms against the HPO vocabulary. |
| **routes/search.py** | Semantic HPO search endpoint (`/search/hpo`). Fuzzy-matches free text to HPO terms using sentence-transformers embeddings (all-MiniLM-L6-v2). |
| **routes/submissions.py** | Patient submission CRUD + doctor review workflow. Validates actor headers (`x-lumina-user-id`, `x-lumina-role`), enforces role-based access control, and handles submission lifecycle. |
| **routes/agent.py** | Agent logic: next-best-question generation, referral letter generation, patient summary generation, and PDF generation. |
| **routes/disease.py** | Disease lookup and differential diagnosis scoring against the Orphanet knowledge graph. |
| **routes/fhir.py** | FHIR export for clinical case data. |
| **score.py** | HPO similarity ranking with Information Content weighted scoring. |
| **pyproject.toml** | Project config: Python 3.13+ dependencies (fastapi, sqlmodel, groq, cyvcf2, extractors, scoring, etc.), local package path references, uv source resolution. |

### Frontend (`apps/web/`)

| File | Purpose |
|------|---------|
| **proxy.ts** | Clerk middleware (`@clerk/nextjs/server`). Protects protected routes (dashboard, cases, intake, patient, etc.) with Clerk auth. Wraps `next-intl/middleware` for internationalization. |
| **lib/api.ts** | API client layer. Functions like `getApiHealth()`, `createPatientSubmissionRemote()`, `getPatientSubmissionsRemote()`, etc. All calls to `/api` endpoints use the `x-lumina-user-id` and `x-lumina-role` headers. |
| **lib/user-role.ts** | Resolves user role from Clerk public metadata or local storage (stored in localStorage for offline sessions). |
| **lib/clerk-localization.ts** | Clerk localization file with 7 language bundles (en, hi, de, fr, es, zh, ja). |
| **lib/formatters.ts** | Data formatting helpers (date formatting, string sanitization, etc.). |
| **lib/utils.ts** | General utility functions used across the frontend. |
| **lib/hpo.ts** | HPO term helper functions. |
| **lib/demo-cases.ts** | Demo clinical case data for testing. |
| **components/lumina/role-guard.tsx** | Role-based access control component. Checks Clerk user role against allowed roles; redirects unauthorized users. |
| **components/lumina/product-page.tsx** | Product display component. |
| **components/lumina/info-page.tsx** | Information display component. |
| **components/lumina/referral-letter-sheet.tsx** | Referral letter sheet component. |
| **i18n/routing.ts** | next-intl routing configuration with 7 locales (en, hi, de, fr, es, zh, ja). |
| **package.json** | Frontend dependencies: Next.js 16, @clerk/nextjs, @clerk/localizations, react-hook-form, zod, etc. |

### Data & Configuration

| File | Purpose |
|------|---------|
| **.env** | Backend environment variables. Contains Supabase `DATABASE_URL` (PostgreSQL connection), `GROQ_API_KEY`, and other backend secrets. Must be configured with actual credentials. |
| **.env.local** | Frontend environment variables. Contains `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, and `NEXT_PUBLIC_API_URL`. |
| **.env.example** | Example `.env` file with placeholder values. Used as a template for new team members. |
| **database_schema_postgres.sql** | Supabase PostgreSQL schema migration. |
| **supabase_migration.sql** | Supabase migration (alternative to the PostgreSQL schema). |

### Databases

| File | Purpose |
|------|---------|
| **data/orpha.sqlite** | Knowledge graph database (read-only, git LFS-tracked). Contains disease, phenotype, gene, and clinical variant data from Orphanet, ClinVar, and FGDD. |
| **data/lumina_app.sqlite** | Application runtime database. Contains submissions, clinical cases, doctor messages, and other runtime state. Auto-created on first boot. |

### Scripts

| File | Purpose |
|------|---------|
| **scripts/build_hpo_index.py** | Builds the HPO embedding index using sentence-transformers (all-MiniLM-L6-v2) for semantic search. |
| **scripts/eval.py** | Evaluation and testing utilities for the scoring pipeline. |
| **scripts/fresh_push.ps1** | PowerShell script for database push. |
| **scripts/train_xgb.py** | XGBoost training script for scoring models. |

### Packages (monorepo)

| Package | Purpose |
|---------|---------|
| **packages/ingest/** | Ingestion pipeline: parses clinical notes, lab reports, photos, and VCF files. Extracts HPO terms and structures clinical evidence. |
| **packages/scoring/** | Scoring engine: HPO similarity ranking (Jaccard, Lin distances) with Information Content weighting and genetic variant scoring. |
| **packages/agent/** | Referral letter generation and agent loop: generates narrative clinical summaries and specialist referral letters. |
| **packages/schemas/** | Shared TypeScript type definitions for all packages. |
| **packages/extractors/** | Extractor packages: separate modules for lab (OCR), notes (LLM), photo (dysmorphology), and VCF parsing. |

### Tests

| File | Purpose |
|------|---------|
| **tests/test_api.py** | API endpoint tests for all routes (intake, score, submissions, agent, disease, search, fhir). |
| **tests/test_ingest.py** | Ingestion pipeline tests for HPO extraction from various data types. |
| **tests/test_scoring.py** | Scoring and ranking logic tests. |
| **tests/conftest.py** | Test fixtures and shared setup. |

### Infrastructure

| File | Purpose |
|------|---------|
| **Dockerfile** | Docker build for the API backend (Python 3.13, tesseract-ocr, uv). Exposes port 7860. |
| **.github/workflows/ci.yml** | CI pipeline for automated testing and deployment. |
| **vercel.json** | Vercel deployment configuration. |
| **pnpm-workspace.yaml** | Monorepo workspace configuration for pnpm. |
| **setup.sh** | All-in-one setup script for the backend (doctor, env, install, db, index, run, health, harden-auth, all). |

### Web Frontend

| File | Purpose |
|------|---------|
| **components/lumina/role-guard.tsx** | Client-side role guard. Checks `user.publicMetadata.role` (from Clerk) against allowed roles. Falls back to localStorage role. Redirects unauthorized users. |
| **lib/user-role.ts** | Reads user role from Clerk public metadata or localStorage. |
| **lib/api.ts** | All API communication. Uses `x-lumina-user-id` and `x-lumina-role` headers for authenticated API calls. |

---

## Authentication & Authorization

### Web Tier (Next.js)
- **Clerk**: Authentication via `@clerk/nextjs` (`clerkMiddleware` in `proxy.ts`).
- Protected routes: `/dashboard`, `/cases`, `/new-case`, `/results`, `/intake`, `/case`, `/patient`, etc.
- User roles stored in `user.publicMetadata.role` or fallback to localStorage via `readStoredUserRole()`.
- API calls from the frontend include `x-lumina-user-id` and `x-lumina-role` headers.

### API Tier (FastAPI)
- **Actor-header gate**: Every protected endpoint validates `x-lumina-user-id` and `x-lumina-role` headers.
- Allowed roles: `doctor`, `patient`.
- Role-based access: patients can create, view, delete their own submissions; doctors can review, modify, and release submissions.
- Optional JWT verification: `setup.sh harden-auth` emits a `security_jwt.py` module for verifying Clerk session tokens.

### Database
- **Knowledge graph**: `data/orpha.sqlite` (Supabase PostgreSQL, read-only, git LFS-tracked).
- **App DB**: `data/lumina_app.sqlite` (SQLite, runtime state, auto-created).

---

## Running the Backend

### Local Development
```bash
cd apps/api
uv sync
uv run uvicorn main:app --reload --port 8000
```

### Docker (production)
```bash
docker build -t lumina-api -f apps/api/Dockerfile apps/api
docker run -p 7860:7860 lumina-api
```

### Vercel (production)
```bash
vercel deploy --prod
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## Key Design Decisions

1. **Role-based auth via headers** — The API uses `x-lumina-user-id` and `x-lumina-role` headers instead of JWT for the current implementation, with optional JWT verification support via `setup.sh harden-auth`.
2. **Separate frontend envs** — `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` are in `apps/web/.env.local`, while `GROQ_API_KEY` is in `apps/api/.env`.
3. **Two SQLite databases** — `orpha.sqlite` is read-only (knowledge graph), `lumina_app.sqlite` is the runtime app database with all clinical state.
4. **Doctor-in-the-loop** — Every AI extraction is presented to the clinician for accept/reject before scoring.
5. **Patient-safe portal** — Only doctor-approved summaries and referral letters are shown to patients; raw technical scores are hidden.