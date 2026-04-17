# Lexora AI

A document question-answering system. Upload PDF, TXT, MD, or DOCX files, then ask questions in natural language. Answers are generated from your documents with source tracking.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| Database ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Vector Store | FAISS |
| AI/LLM | LangChain + OpenAI |
| Cache | Redis |
| Task Queue | Celery |

## Features

- JWT authentication with access and refresh tokens
- Document upload and processing (PDF, TXT, MD, DOCX)
- Smart text chunking with configurable overlap
- Vector storage with per-user isolation
- RAG-powered chat with source attribution
- Streaming responses via Server-Sent Events
- Persistent chat history per conversation
- Redis caching for retrieval results
- Prometheus metrics endpoint
- Health checks (liveness and readiness)
- Structured JSON logging

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (optional)
- OpenAI API key

## Installation

```bash
git clone https://github.com/neuralbroker/lexora-ai.git
cd lexora-ai

python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\bin\bat                  # Windows

pip install -r requirements.txt

cp .env.example .env
# edit .env with your credentials

docker-compose -f docker/docker-compose.yml up -d

uvicorn app.main:app --reload
```

API available at http://localhost:8000
API docs at http://localhost:8000/docs

## Usage

**Register a new user**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register -H Content-Type:application/json -d '{\"email\":\"user@example.com\",\"password\":\"yourpassword\"}'
```

**Login (returns access_token and refresh_token)**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login -d username=user@example.com -d password=yourpassword
```

**Upload a document**
```bash
curl -X POST http://localhost:8000/api/v1/documents -H Authorization:Bearer YOUR_TOKEN -F file=@path/to/document.pdf
```

**List your documents**
```bash
curl http://localhost:8000/api/v1/documents -H Authorization:Bearer YOUR_TOKEN
```

**Send a chat message (streaming response)**
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream -H Authorization:Bearer YOUR_TOKEN -H Content-Type:application/json -d '{\"message\":\"What is this document about?\"}'
```

**Send a chat message (non-streaming)**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message -H Authorization:Bearer YOUR_TOKEN -H Content-Type:application/json -d '{\"message\":\"What is this document about?\"}'
```

**List conversations**
```bash
curl http://localhost:8000/api/v1/chat/conversations -H Authorization:Bearer YOUR_TOKEN
```

## Project Structure

```
lexora-ai/
|
+- app/                    Main application package
|   +- api/v1/             REST API endpoints (auth, documents, chat)
|   +- core/               Security, exceptions, logging
|   +- models/             Pydantic request/response schemas
|   +- schemas/            SQLAlchemy database models
|   +- services/           Business logic layer
|   |   +- document_service.py   Document upload and processing
|   |   +- chat_service.py       Chat orchestration
|   |   +- llm_service.py        OpenAI GPT integration
|   |   +- vector_service.py     FAISS vector operations
|   |   +- cache_service.py      Redis caching
|   |   +- embedding_service.py  OpenAI embeddings
|   |   +- retrieval_service.py  Context retrieval
|   |
|   +- tasks/              Celery background tasks
|   +- utils/              Text chunking, document parsing
|   +- main.py             FastAPI application entry point
|   +- config.py           Configuration management
|   +- deps.py             Dependency injection
|
+- tests/                  Test suite
|   +- unit/               Unit tests
|   +- conftest.py         Test fixtures and setup
|
+- docker/                 Docker configuration
|   +- Dockerfile          Application container image
|   +- docker-compose.yml  Local development stack
|
+- .env.example            Environment variables template
+- requirements.txt        Python dependencies
+- pyproject.toml          Project configuration
+- pytest.ini              Test configuration
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql+asyncpg://user:pass@localhost:5432/lexora |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| SECRET_KEY | JWT signing key (min 32 chars) | your-super-secret-key-here |
| OPENAI_API_KEY | OpenAI API key for GPT and embeddings | sk-... |
| OPENAI_MODEL | GPT model name | gpt-4-turbo-preview |
| OPENAI_EMBEDDING_MODEL | Embedding model name | text-embedding-3-small |
| CELERY_BROKER_URL | Celery broker URL | redis://localhost:6379/1 |
| CELERY_RESULT_BACKEND | Celery result backend URL | redis://localhost:6379/2 |
| FAISS_INDEX_PATH | Directory for FAISS indexes | ./data/faiss |
| UPLOAD_DIR | Directory for uploaded files | ./uploads |
| MAX_FILE_SIZE | Max upload size in bytes | 52428800 |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License