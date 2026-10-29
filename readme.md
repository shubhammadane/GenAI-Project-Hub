# EasyResearch

> **AI-Powered Research Paper Discovery and Analysis Platform**  
> Final Year B.Tech Computer Science and Engineering Project

---

## Project Overview

EasyResearch is a complete AI-powered platform that simplifies the discovery, understanding, comparison, and analysis of academic research papers. It is **not** just a PDF chatbot — it is a full research assistant combining Retrieval-Augmented Generation (RAG), semantic search, multi-paper comparison, research gap detection, and trend analysis.

---

## Features

| Feature | Status |
|---------|--------|
| User authentication (JWT) | ✅ Phase 2 |
| Paper upload + metadata | ✅ Phase 3 |
| PDF parsing + section detection | ✅ Phase 4 |
| Chunking + embeddings | ✅ Phase 5 |
| Vector DB (ChromaDB) | ✅ Phase 5 |
| Semantic search | ✅ Phase 5 |
| RAG Q&A with evidence | ✅ Phase 6 |
| Paper summarization | ✅ Phase 7 |
| Multi-paper comparison | 🔄 Phase 8 |
| Research gap detection | 🔄 Phase 9 |
| Research trend analysis | 🔄 Phase 9 |
| Knowledge graph | ⏳ Phase 11 |
| Agentic workflow | ⏳ Phase 10 |
| Docker deployment | ⏳ Phase 12 |

---

## Architecture

```
React Frontend (Vite + Tailwind)
         |
         | REST API (/api)
         ↓
Node.js + Express Backend (:5000)
         |
    ─────────────────────────
    |                        |
    ↓                        ↓
MongoDB                Python FastAPI AI Service (:8000)
(metadata)              |
                   ─────────────────────────
                   |          |            |
                   ↓          ↓            ↓
                PDF Parser  Embeddings   LLM (configurable)
                              |
                           ChromaDB
                           (vectors)
                              |
                           RAG → Answer + Sources

Python FastAPI Research Engine (:8001)
   Consumes AI Service APIs for:
   - Multi-paper comparison
   - Gap detection
   - Trend analysis
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS v4 |
| Routing | React Router v6 |
| HTTP Client | Axios |
| Charts | Recharts |
| Graph Viz | React Flow |
| Main Backend | Node.js, Express.js |
| Database | MongoDB, Mongoose |
| Auth | JWT (jsonwebtoken), bcryptjs |
| File Upload | Multer |
| AI Service | Python, FastAPI, Uvicorn |
| PDF Parsing | PyMuPDF, pdfplumber |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector DB | ChromaDB |
| LLM | Gemini (default) / OpenAI / Groq — configurable |
| Research Engine | Python, FastAPI |

---

## Repository Structure

```
EasyResearch/
├── frontend/               ← Member 4 — React + Vite + Tailwind
│   └── src/
│       ├── api/            ← Axios API modules
│       ├── components/     ← Reusable UI components
│       ├── context/        ← Auth context
│       └── pages/          ← All page components
│
├── backend/                ← Member 1 — Node.js + Express
│   └── src/
│       ├── config/         ← DB connection
│       ├── controllers/    ← Request handlers
│       ├── middleware/      ← Auth, upload, errors
│       ├── models/         ← Mongoose schemas
│       ├── routes/         ← Express routes
│       └── utils/          ← JWT helpers
│
├── ai-service/             ← Member 2 — Python + FastAPI
│   └── app/
│       ├── routers/        ← FastAPI endpoints
│       ├── services/       ← PDF parser, chunker, embeddings, vector store, LLM
│       └── config.py       ← Settings (pydantic-settings)
│
├── research-engine/        ← Member 3 — Python + FastAPI
│   └── app/
│       ├── routers/        ← compare, gaps, trends, health
│       └── config.py
│
├── docs/
│   ├── API.md              ← Complete API contract
│   └── GIT_WORKFLOW.md     ← Git branching strategy
│
├── .gitignore
├── .env.example
├── docker-compose.yml
└── README.md               ← This file
```

---

## Team Responsibilities

| Member | Role | Primary Directory |
|--------|------|-------------------|
| Member 1 | Backend + Database | `/backend` |
| Member 2 | AI / ML / RAG | `/ai-service` |
| Member 3 | Research Intelligence | `/research-engine` |
| Member 4 | UI / UX / Frontend | `/frontend` |

---

## Installation & Setup

### Prerequisites

- Node.js v20+
- Python 3.11+
- MongoDB (local or MongoDB Atlas)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/gangaprasad29/Easy-Research.git
cd Easy-Research
```

### 2. Setup the Backend (Member 1)

```bash
cd backend
cp .env.example .env
# Edit .env and fill in MONGODB_URI, JWT_SECRET
npm install
npm run dev
```

### 3. Setup the AI Service (Member 2)

```bash
cd ai-service
cp .env.example .env
# Edit .env: set LLM_PROVIDER and relevant API key (GOOGLE_API_KEY, etc.)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Setup the Research Engine (Member 3)

```bash
cd research-engine
cp .env.example .env
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### 5. Setup the Frontend (Member 4)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## Environment Variables

Copy `.env.example` to `.env` in each module and fill in values.

| Variable | Module | Description |
|----------|--------|-------------|
| `MONGODB_URI` | backend | MongoDB connection string |
| `JWT_SECRET` | backend | JWT signing secret (min 32 chars) |
| `LLM_PROVIDER` | ai-service | `gemini`, `openai`, or `groq` |
| `GOOGLE_API_KEY` | ai-service | Gemini API key |
| `OPENAI_API_KEY` | ai-service | OpenAI API key |
| `GROQ_API_KEY` | ai-service | Groq API key |
| `EMBEDDING_MODEL` | ai-service | SentenceTransformer model name |
| `CHROMA_HOST` | ai-service | ChromaDB host |

**⚠ Never commit real `.env` files to Git.**

---

## Development Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Foundation — repo structure, all service scaffolds | ✅ Complete |
| Phase 2 | Authentication — register, login, JWT, protected routes | ✅ Complete |
| Phase 3 | Paper Management — upload, metadata, listing, deletion | ✅ Complete |
| Phase 4 | Document Intelligence — PDF parsing, section detection, chunking | ✅ Complete |
| Phase 5 | Semantic Search — embeddings, ChromaDB, vector search | ✅ Complete |
| Phase 6 | RAG — retrieval, context construction, LLM, answer + evidence | ✅ Complete |
| Phase 7 | Summarization — paper, section, methodology, results, conclusion | ✅ Complete |
| Phase 8 | Multi-Paper Analysis — comparison table | 🔄 Scaffold ready |
| Phase 9 | Research Intelligence — gaps, trends, recommendations | 🔄 Scaffold ready |
| Phase 10 | Agentic Workflow | ⏳ Pending |
| Phase 11 | Visualization — charts, knowledge graph | ⏳ Pending |
| Phase 12 | Testing & Deployment — Docker, CI, docs | ⏳ Pending |

---

## Git Branching Strategy

```
main → develop → feature/backend-auth
                 feature/rag-pdf-parser
                 feature/research-comparison
                 feature/frontend-dashboard
```

See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md) for full rules.

---

## Tasks Completed (Phase 1 Foundation)

**Repository & Configuration**
- [x] Created full monorepo folder structure
- [x] Root `.gitignore` (excludes .env, node_modules, __pycache__, uploads, vector DBs)
- [x] Root `.env.example` with all required variables documented
- [x] `docker-compose.yml` for MongoDB, ChromaDB, all four services

**Backend (Member 1 — Node.js/Express)**
- [x] `server.js` — Express entry point
- [x] `src/app.js` — Middleware, CORS, rate limiting, routes
- [x] `src/config/db.js` — Mongoose connection
- [x] `src/models/User.js` — bcrypt hashing, safe JSON, comparison method
- [x] `src/models/Paper.js` — Full paper schema with indexes
- [x] `src/models/ChatSession.js` — Session + messages with source evidence
- [x] `src/middleware/authMiddleware.js` — JWT Bearer validation
- [x] `src/middleware/uploadMiddleware.js` — Multer PDF validation
- [x] `src/middleware/errorMiddleware.js` — Central error handler
- [x] `src/utils/jwt.js` — Sign/verify helpers
- [x] `src/routes/authRoutes.js` + `authController.js` — Register, login, getMe, updateProfile
- [x] `src/routes/paperRoutes.js` + `paperController.js` — Upload, list, get, delete, status
- [x] `src/routes/searchRoutes.js` + `searchController.js` — Keyword + semantic search
- [x] `src/routes/aiRoutes.js` + `aiController.js` — RAG ask, summarize, AI status

**AI Service (Member 2 — Python/FastAPI)**
- [x] `main.py` — Uvicorn entry point
- [x] `app/main.py` — FastAPI factory with CORS, all routers
- [x] `app/config.py` — Pydantic settings (LLM, embeddings, vector DB, storage)
- [x] `app/services/pdf_parser.py` — PyMuPDF parser with section detection heuristics
- [x] `app/services/chunker.py` — Sliding-window chunker with overlap, full metadata
- [x] `app/services/embeddings.py` — SentenceTransformer singleton loader
- [x] `app/services/vector_store.py` — ChromaDB wrapper (store, retrieve, delete)
- [x] `app/services/llm.py` — Configurable LLM provider (Gemini/OpenAI/Groq)
- [x] `app/routers/health.py` — Health check
- [x] `app/routers/process.py` — PDF processing pipeline endpoint
- [x] `app/routers/ask.py` — RAG endpoint (retrieve → LLM → answer + sources)
- [x] `app/routers/summarize.py` — Type-specific summarization
- [x] `app/routers/search.py` — Semantic search over all vectors

**Research Engine (Member 3 — Python/FastAPI)**
- [x] `main.py` — Uvicorn entry point (:8001)
- [x] `app/main.py` — FastAPI factory
- [x] `app/config.py` — Settings
- [x] `app/routers/compare.py` — Multi-paper dimension comparison (calls AI service)
- [x] `app/routers/gaps.py` — Research gap detection from paper limitations
- [x] `app/routers/trends.py` — Year/keyword/topic trend aggregation
- [x] `app/routers/health.py` — Health check

**Frontend (Member 4 — React/Vite/Tailwind)**
- [x] Vite + React scaffold with Tailwind CSS v4
- [x] `vite.config.js` — Tailwind plugin + API proxy
- [x] `src/index.css` — Complete design system (dark theme, glassmorphism, components)
- [x] `src/api/client.js` — Axios with JWT interceptor + 401 redirect
- [x] `src/api/index.js` — Typed API modules (auth, papers, search, ai)
- [x] `src/context/AuthContext.jsx` — Auth state, login/register/logout, session persistence
- [x] `src/components/ProtectedRoute.jsx` — Auth guard with loading spinner
- [x] `src/components/Sidebar.jsx` — Full navigation sidebar
- [x] `src/components/AppLayout.jsx` — Sidebar + main content layout
- [x] `src/pages/LandingPage.jsx` — Hero, features grid, CTA
- [x] `src/pages/LoginPage.jsx` — Login form with error handling
- [x] `src/pages/RegisterPage.jsx` — Registration form
- [x] `src/pages/DashboardPage.jsx` — Stats, quick actions, recent papers
- [x] `src/pages/SearchPage.jsx` — Keyword/semantic search with results
- [x] `src/pages/UploadPage.jsx` — Drag-and-drop PDF upload with metadata
- [x] `src/pages/PaperDetailPage.jsx` — Paper info, sections, summary generator
- [x] `src/pages/AssistantPage.jsx` — RAG chat with source evidence
- [x] `src/pages/PlaceholderPages.jsx` — Compare, Gaps, Trends, KG, History, Profile

**Documentation**
- [x] `docs/API.md` — Complete API contract for all four services
- [x] `docs/GIT_WORKFLOW.md` — Branching strategy, commit format, PR rules

---

## API Documentation

See [`docs/API.md`](docs/API.md) for complete API contracts.

---

## Contributing

Follow the Git workflow in [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

Each team member works in their assigned directory.  
All changes go through Pull Requests into `develop`.  
Never commit directly to `main`.

---

## License

Academic use only — Final Year B.Tech CSE Project.
