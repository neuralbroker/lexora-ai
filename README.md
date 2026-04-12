# Lexora AI

<p align="center">
  <strong>Enterprise Knowledge Intelligence Platform</strong><br />
  Build AI-powered document Q&A systems with production-grade architecture
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.109+-00a393?style=flat&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License" />
  <img src="https://img.shields.io/github/stars/sajadkoder/lexora-ai?style=flat" alt="Stars" />
</p>

---

## Overview

Lexora AI is an enterprise-grade knowledge intelligence platform that enables:
- Upload documents (PDF, TXT, MD, DOCX)
- Ask natural language questions
- Get accurate, sourced answers using RAG (Retrieval-Augmented Generation)

### Tech Stack

| Component | Technology |
|-----------|------------|
| API | FastAPI + AsyncIO |
| Database | PostgreSQL + SQLAlchemy |
| Vector Store | FAISS |
| AI/LLM | LangChain + OpenAI |
| Cache | Redis |
| Tasks | Celery |
| Auth | JWT (python-jose) |

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/sajadkoder/lexora-ai.git
cd lexora-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database, Redis, and OpenAI credentials

# Start services
docker-compose -f docker/docker-compose.yml up -d

# Run the app
uvicorn app.main:app --reload
```

### Endpoints

| Endpoint | Description |
|----------|-------------|
| [http://localhost:8000/docs](http://localhost:8000/docs) | API Documentation |
| [http://localhost:8000/health](http://localhost:8000/health) | Health Check |
| [http://localhost:8000/metrics](http://localhost:8000/metrics) | Prometheus Metrics |

---

## Project Structure

```
lexora-ai/
├── app/
│   ├── api/v1/          # API endpoints (auth, documents, chat)
│   ├── core/            # Security, exceptions, logging
│   ├── models/          # Pydantic schemas
│   ├── schemas/         # SQLAlchemy models
│   ├── services/        # Business logic
│   │   ├── document_service.py    # Document processing
│   │   ├── chat_service.py        # Chat orchestration
│   │   ├── llm_service.py         # OpenAI integration
│   │   ├── vector_service.py      # FAISS operations
│   │   └── cache_service.py       # Redis caching
│   └── utils/           # Text chunking, document parsing
├── tests/               # Unit and integration tests
├── docker/              # Docker configuration
└── requirements.txt     # Dependencies
```

---

## API Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=password123"
```

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

### Chat (Streaming)
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this document about?"}'
```

---

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | GPT model (default: gpt-4-turbo-preview) | No |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (default: text-embedding-3-small) | No |

---

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test file
pytest tests/unit/test_auth.py -v
```

---

## Deployment

### Docker
```bash
# Build
docker build -t lexora-ai -f docker/Dockerfile .

# Run
docker run -d -p 8000:8000 -e DATABASE_URL=... -e REDIS_URL=... lexora-ai
```

### Docker Compose
```bash
docker-compose -f docker/docker-compose.yml up -d
```

---

## Features

- JWT Authentication with refresh tokens
- Document upload (PDF, TXT, MD, DOCX)
- Smart text chunking with overlap
- FAISS vector storage with user isolation
- RAG pipeline with source tracking
- Streaming responses (Server-Sent Events)
- Chat history persistence
- Redis caching
- Prometheus metrics
- Health checks (liveness + readiness)
- Structured logging

---

## Scaling

For 10k+ users:
- Deploy multiple API instances behind load balancer
- Add PostgreSQL read replicas
- Migrate FAISS to Pinecone/Weaviate
- Scale Celery workers
- Use Redis Cluster

---

## License

MIT License

---

## Author

Built by [Sajad](https://github.com/sajadkoder)