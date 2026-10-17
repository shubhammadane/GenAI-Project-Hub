# 🎙️ AI Meeting Intelligence Platform

<p align="center">
  <img src="Source Code\docs\AI-Meeting Platform.png" alt="AI Meeting Intelligence Platform Architecture" width="100%">
</p>

<p align="center">
  <strong>Convert meeting recordings into an intelligent, searchable organizational knowledge base using Speech-to-Text, Vector Search, Retrieval-Augmented Generation (RAG), and Large Language Models.</strong>
</p>

---

## 📌 Overview

Meetings often contain valuable discussions, decisions, and action items that become difficult to revisit later.

The **AI Meeting Intelligence Platform** aims to solve this problem by allowing users to upload meeting recordings and interact with them using natural language.

Instead of manually watching hours of recordings, users can simply ask questions like:

- *What decisions were made?*
- *What did John say about PostgreSQL?*
- *What was discussed after 15 minutes?*
- *Summarize the entire meeting.*

The system converts meeting recordings into searchable vector embeddings and uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware answers.

---

# 🚧 Current Project Status

> **Project Stage:** Early Development

### ✅ Currently Implemented

- Video Upload
- Audio Extraction using FFmpeg
- Speech-to-Text using Whisper
- Transcript JSON Generation
- Transcript Chunking
- Embedding Generation (BGE-M3)
- Vector Storage using Qdrant
- Semantic Search
- Basic RAG Question Answering

---

## 🏗 Current Workflow

```
Video
   │
   ▼
FFmpeg
   │
   ▼
Whisper
   │
   ▼
Transcript (JSON)
   │
   ▼
Chunking
   │
   ▼
Embeddings (BGE-M3)
   │
   ▼
Qdrant
   │
   ▼
Vector Search
   │
   ▼
LLM
   │
   ▼
Answer
```

---

# 🏛 Planned System Architecture

The image below represents the complete vision of the project.

Currently, the implementation covers only the **AI Processing Pipeline** and **RAG Flow**.

Future development will include:

- FastAPI Backend
- Next.js Frontend
- Authentication
- PostgreSQL
- Meeting Intelligence Layer
- Kafka-based Scalable Processing
- Docker Deployment

---

# 🧠 Core Features (Planned)

### Meeting Intelligence

- Executive Summaries
- Topic Detection
- Decision Extraction
- Action Item Extraction
- Sentiment Analysis
- Deadline Detection
- Speaker Identification
- Cross-Meeting Search

---

### AI Chat

Users can ask questions like:

> What decisions were taken?

> Who is responsible for Task 4?

> Summarize the discussion about authentication.

> What happened between 12:00 and 15:00?

---

### Workspace Features

- Multiple Workspaces
- Meeting History
- Search Across Meetings
- Export Summary
- Role-Based Access

---

# ⚙️ Tech Stack

| Category | Technology |
|------------|------------|
| Language | Python |
| Speech-to-Text | Whisper |
| Audio Processing | FFmpeg |
| Embeddings | BGE-M3 |
| Vector Database | Qdrant |
| LLM | Ollama *(Planned)* |
| Backend | FastAPI *(Planned)* |
| Frontend | Next.js *(Planned)* |
| Database | PostgreSQL *(Planned)* |
| Authentication | JWT *(Planned)* |
| Event Streaming | Kafka *(Planned)* |
| Cache | Redis *(Planned)* |
| Deployment | Docker *(Planned)* |

---

# 📂 Project Structure

```
AI-Meeting-Intelligence/

│
├── uploads/
│
├── transcripts/
│
├── embeddings/
│
├── vector_db/
│
├── rag/
│
├── docs/
│   └── architecture.png
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

# 📈 Development Roadmap

## ✅ Phase 1 (Current)

- [x] Video Upload
- [x] Audio Extraction
- [x] Whisper Transcription
- [x] JSON Transcript
- [x] Embeddings
- [x] Qdrant Integration
- [x] Semantic Search
- [x] Basic Question Answering

---

## 🚧 Phase 2

- [ ] Better Chunking Strategy
- [ ] Metadata Storage
- [ ] Prompt Engineering
- [ ] Timestamp Citations
- [ ] Source Chunk Display
- [ ] Retrieval Optimization

---

## 🚧 Phase 3

Meeting Intelligence Layer

- [ ] Executive Summary
- [ ] Action Item Extraction
- [ ] Decision Detection
- [ ] Topic Detection
- [ ] Sentiment Analysis

---

## 🚧 Phase 4

Backend Development

- [ ] FastAPI
- [ ] REST APIs
- [ ] PostgreSQL
- [ ] Authentication
- [ ] Meeting Management APIs

---

## 🚧 Phase 5

Frontend Development

- [ ] Next.js Dashboard
- [ ] AI Chat
- [ ] Meeting Upload
- [ ] Meeting History
- [ ] Workspace Management

---

## 🚧 Phase 6

Production Ready

- [ ] Docker
- [ ] Redis
- [ ] Kafka Workers
- [ ] Cloud Deployment

---

# 🎯 Learning Objectives

This project is being built to gain hands-on experience with modern AI systems, including:

- Retrieval-Augmented Generation (RAG)
- Vector Databases
- Semantic Search
- Embedding Models
- Prompt Engineering
- Large Language Models
- FastAPI
- Next.js
- PostgreSQL
- Docker
- Kafka
- Redis
- Production AI Architecture

---

# 🔮 Future Vision

The final goal is to build a production-ready SaaS platform where organizations can:

- Upload meeting recordings
- Automatically generate meeting summaries
- Detect decisions and action items
- Search across thousands of meetings
- Chat with meeting history using AI
- Collaborate within workspaces
- Export reports
- Scale using distributed workers

---

# 📜 License

This project is licensed under the MIT License.

---

## ⭐ If you found this project interesting, consider giving it a Star!
