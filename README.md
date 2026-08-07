# Lumina

**Doctor-reviewed rare disease triage, phenotype scoring, and patient-safe referral generation**

[![Frontend](https://img.shields.io/badge/frontend-Next.js%2016-black?style=flat-square)](apps/web)
[![API](https://img.shields.io/badge/API-FastAPI-green?style=flat-square)](apps/api)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)](apps/api)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](#)

---

## 📌 Overview

Lumina is a clinical decision-support platform designed to shorten the rare disease diagnostic odyssey. It converts scattered clinical notes, lab reports, genetic VCF files, and medical photographs into doctor-reviewed Human Phenotype Ontology (HPO) findings, ranks candidate rare diseases against Orphanet/HPO knowledge graphs, and generates single-page specialist referral letters.

Lumina operates on a strict **Doctor-in-the-Loop** principle:
- AI extracts candidate clinical phenotypes from multimodal evidence.
- Clinicians must explicitly accept or reject every suggested phenotype.
- Rejected and pending phenotypes are excluded from disease differential scoring.
- Genetic evidence is integrated to provide diagnostic weighting.
- Patients receive clinician-approved referral documentation without exposing raw technical differential rankings.

> 🎤 **Presenting at a Hackathon?** Read our complete 3-minute pitch presentation script in [pitch.md](pitch.md).

---

## ⚡ Quick Start & Local Setup

### Prerequisites

Ensure you have the following installed on your machine:
- **Node.js**: v20 or higher
- **pnpm**: v9 or higher (`npm install -g pnpm`)
- **Python**: v3.12 or v3.13
- **uv** (recommended for fast Python package management): `pip install uv`

---

### 1. Clone & Install Repository Dependencies

```bash
# Clone the repository
git clone https://github.com/vees-1/lumina.git
cd lumina

# Install frontend monorepo dependencies
pnpm install
```

---

### 2. Start Backend API Server

Open a terminal window for the API backend:

```bash
cd apps/api

# Option A: Using uv (Recommended)
uv sync
uv run uvicorn main:app --reload --port 8000

# Option B: Using standard Python venv
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -e ../../packages/ingest -e ../../packages/scoring -e ../../packages/extractors -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API server will run at `http://localhost:8000`. You can inspect API interactive documentation at `http://localhost:8000/docs`.

---

### 3. Start Frontend Web Application

Open a second terminal window in the root repository directory:

```bash
# Start Next.js frontend dev server
pnpm --filter web dev
```

The web application will run at `http://localhost:3000`.

---

### 4. Environment Configuration

#### Backend Environment (`apps/api/.env`)
Create an `.env` file inside `apps/api/.env` if using external LLM or extraction keys:
```env
GROQ_API_KEY=your_groq_api_key_here
```

#### Frontend Environment (`apps/web/.env.local`)
Create an `.env.local` file inside `apps/web/.env.local`:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🛠️ Repository Structure

```
lumina/
├── apps/
│   ├── api/             # FastAPI service (routing, intake endpoints, health check)
│   └── web/             # Next.js 16 frontend (Intake, Case View, Referral Letter, Demo)
├── packages/
│   ├── agent/           # Referral letter generation & agent loop logic
│   ├── extractors/      # Multimodal clinical note, photo, lab, and VCF extractors
│   ├── ingest/          # Knowledge graph models for HPO, Orphanet, ClinVar & FGDD
│   ├── schemas/         # Shared TypeScript schemas
│   └── scoring/         # HPO similarity ranker & Information Content scoring engine
├── pitch.md             # 3-Minute hackathon pitch script & live demo flow
└── scripts/             # Indexing scripts and evaluation utilities
```

---

## 🎯 Key Application Features

1. **Multimodal Intake Workspace (`/intake`)**: Upload clinical notes, voice recordings, lab reports, genetic VCF files, and patient images.
2. **Doctor Phenotype Review**: Interactive chips allow clinicians to accept accurate HPO terms and reject false suggestions.
3. **Ontology Differential Scoring (`/case/[id]`)**: Ranks candidate rare diseases using semantic similarity metrics (Jaccard and Lin distances) combined with genetic variant weighting.
4. **Specialist Referral Generator (`/case/[id]/letter`)**: Generates an editable, single-page referral letter for specialist handoff.
5. **Patient Dashboard**: Safe portal displaying doctor-released summaries and referral letters without raw technical scorecards.
6. **Curated Demo Suite (`/demo`)**: Pre-configured clinical cases ready for live judging and testing.

---

## 📜 License

This project is licensed under the MIT License. Lumina is a research prototype intended for clinical decision support and is not a certified medical device.
