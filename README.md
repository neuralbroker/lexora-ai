# Lexora AI

<p align="center">
  <img src="https://via.placeholder.com/150x150?text=Lexora" alt="Lexora AI Logo" />
</p>

<p align="center">
  Enterprise Knowledge Intelligence Platform
</p>

<p align="center">
  <a href="https://github.com/your-org/lexora-ai/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/your-org/lexora-ai/ci.yml" alt="CI" />
  </a>
  <a href="https://pypi.org/project/lexora-ai/">
    <img src="https://img.shields.io/pypi/v/lexora-ai" alt="PyPI" />
  </a>
  <a href="https://pepy.tech/badge/lexora-ai">
    <img src="https://pepy.tech/badge/lexora-ai" alt="Downloads" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/lexora-ai" alt="License" />
  </a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Security](#security)
- [Monitoring](#monitoring)
- [Scaling](#scaling)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Lexora AI** is an enterprise-grade knowledge intelligence platform that enables organizations to upload documents (PDFs, text files, Word documents), ask natural language questions, and receive accurate, sourced answers using Retrieval-Augmented Generation (RAG).

### Why Lexora AI?

- **Enterprise-Ready**: Production-grade code with proper error handling, logging, and monitoring
- **Scalable Architecture**: Designed to handle 10k+ users with horizontal scaling
- **Privacy-First**: All data is isolated per-user with secure authentication
- **Modern Stack**: Built with FastAsyncIO, LangChain, and vector databases
- **Developer Experience**: Comprehensive API docs, type hints, and testing

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Document Upload** | Support for PDF, TXT, MD, DOCX files up to 50MB |
| **Text Extraction** | Intelligent text extraction with layout preservation |
| **Smart Chunking** | Semantic text chunking with overlap for context preservation |
| **Vector Embeddings** | OpenAI embeddings with FAISS vector storage |
| **RAG Pipeline** | Retrieval-Augmented Generation with source tracking |
| **Streaming Responses** | Real-time streaming via Server-Sent Events (SSE) |
| **Chat History** | Persistent conversation history per user |
| **JWT Authentication** | Secure token-based authentication with refresh tokens |

### Technical Features

| Feature | Description |
|---------|-------------|
| **Async Processing** | Non-blocking document processing with Celery |
| **Caching Layer** | Redis caching for embeddings and frequent queries |
| **Structured Logging** | JSON logging with correlation IDs |
| **Health Checks** | Liveness and readiness probes |
| **Prometheus Metrics** | Built-in metrics endpoint |
| **Error Handling** | Custom exception hierarchy with proper HTTP codes |
| **Rate Limiting** | Configurable rate limiting per user |

---

## Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │ Mobile App  │  │   API      │  │   CLI       │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼───────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                    │
│                    (Authentication, Rate Limiting, Routing)                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  FastAPI App   │    │  Celery Workers │    │   Monitoring    │
│  (Port 8000)   │    │  (Async Tasks)  │    │   (Prometheus)  │
└────────┬────────┘    └────────┬────────┘    └─────────────────┘
         │                      │
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis      │
│  (Metadata)     │    │  (Cache/Queue)  │
└────────┬────────┘    └────────┬────────┘
         │                      │
         │                      ▼
         │              ┌─────────────────┐
         │              │ FAISS Vector DB │
         │              │ (Embeddings)    │
         │              └─────────────────┘
         │
         ▼
  ┌─────────────────┐
  │  S3/Local Store │
  │  (Documents)    │
  └─────────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. UPLOAD                                                                  │
│     ┌──────────┐     ┌──────────────┐                                       │
│     │  Client  │────▶│  FastAPI     │────▶ Save file to disk/S3            │
│     └──────────┘     └──────────────┘                                       │
│                            │                                                 │
│                            ▼                                                 │
│  2. PROCESS (Async)                                                        │
│     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│     │   Celery     │────▶│  Extract     │────▶│   Chunk      │            │
│     │   Task       │     │   Text       │     │   Text       │            │
│     └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                       │                     │
│                                                       ▼                     │
│  3. EMBED & STORE                                                         │
│     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│     │   Generate   │────▶│   Store in    │────▶│   Update     │            │
│     │   Embedding  │     │   FAISS       │     │   Database   │            │
│     └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                             │
│  4. QUERY                                                                 │
│     ┌──────────┐     ┌──────────────┐     ┌──────────────┐               │
│     │  Client  │────▶│   Retrieve   │────▶│    Generate  │               │
│     │  Query   │     │   Context    │     │    Answer    │               │
│     └──────────┘     └──────────────┘     └──────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.109+ | Web framework |
| **SQLAlchemy** | 2.0+ | ORM |
| **asyncpg** | 0.29+ | PostgreSQL driver |
| **Pydantic** | 2.5+ | Data validation |

### AI & ML

| Technology | Version | Purpose |
|------------|---------|---------|
| **LangChain** | 0.1+ | RAG orchestration |
| **OpenAI** | 1.10+ | LLM & embeddings |
| **FAISS** | 1.7+ | Vector database |
| **Tiktoken** | 0.5+ | Tokenization |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **PostgreSQL** | Metadata & chat history |
| **Redis** | Caching & Celery broker |
| **Docker** | Containerization |
| **Celery** | Async task queue |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/lexora-ai.git
cd lexora-ai
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 5. Start Services

```bash
# Using Docker Compose (recommended)
docker-compose -f docker/docker-compose.yml up -d

# Or start PostgreSQL and Redis manually
```

#### 6. Run Database Migrations

```bash
alembic upgrade head
```

#### 7. Start the Application

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 8. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

---

## Project Structure

```
lexora-ai/
├── app/
│   ├── __init__.py              # Application package
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── deps.py                  # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # API v1 router
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── documents.py   # Document endpoints
│   │   │   └── chat.py         # Chat endpoints
│   │   │
│   │   └── dependencies.py    # API-level dependencies
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py          # JWT, password hashing
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging.py          # Logging configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # Pydantic models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_service.py    # Document processing
│   │   ├── embedding_service.py   # Embedding generation
│   │   ├── vector_service.py      # FAISS operations
│   │   ├── retrieval_service.py  # Context retrieval
│   │   ├── llm_service.py        # LLM integration
│   │   ├── chat_service.py       # Chat orchestration
│   │   └── cache_service.py      # Redis caching
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── document_processor.py # Celery tasks
│   │   └── worker.py             # Worker config
│   │
│   └── utils/
│       ├── __init__.py
│       ├── text_chunker.py       # Text chunking
│       ├── document_parser.py    # PDF/TXT parsing
│       └── helpers.py            # Utilities
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Test fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_text_chunker.py
│   │   └── test_services.py
│   └── integration/
│       ├── __init__.py
│       └── test_api.py
│
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   └── docker-compose.yml
│
├── scripts/
│   ├── init_db.py
│   └── seed_data.py
│
├── alembic/
│   └── versions/                  # Database migrations
│
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── pytest.ini
├── alembic.ini
├── DEPLOYMENT.md
└── README.md
```

---

## API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (get tokens) |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Get current user |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/documents` | List documents |
| POST | `/api/v1/documents` | Upload document |
| GET | `/api/v1/documents/{id}` | Get document |
| GET | `/api/v1/documents/{id}/status` | Get processing status |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chat/conversations` | List conversations |
| POST | `/api/v1/chat/conversations` | Create conversation |
| GET | `/api/v1/chat/conversations/{id}` | Get messages |
| DELETE | `/api/v1/chat/conversations/{id}` | Delete conversation |
| POST | `/api/v1/chat/message` | Send message (sync) |
| POST | `/api/v1/chat/stream` | Send message (streaming) |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/metrics` | Prometheus metrics |

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `APP_NAME` | Application name | No | Lexora AI |
| `ENVIRONMENT` | Environment | No | development |
| `DEBUG` | Debug mode | No | false |
| `DATABASE_URL` | PostgreSQL URL | Yes | - |
| `REDIS_URL` | Redis URL | Yes | - |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `ALGORITHM` | JWT algorithm | No | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | No | 30 |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | LLM model | No | gpt-4-turbo-preview |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | No | text-embedding-3-small |
| `UPLOAD_DIR` | Upload directory | No | ./uploads |
| `MAX_FILE_SIZE` | Max file size (bytes) | No | 52428800 |
| `FAISS_INDEX_PATH` | Vector store path | No | ./data/faiss |
| `CELERY_BROKER_URL` | Celery broker | Yes | - |

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    chunk_count INTEGER DEFAULT 0,
    vector_ids TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py

# Run in watch mode
pytest --watch
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 .
mypy .

# All checks
pre-commit run --all-files
```

### Adding New Features

1. Create a new service in `app/services/`
2. Add Pydantic models in `app/models/`
3. Create API endpoints in `app/api/v1/`
4. Add tests in `tests/`
5. Update documentation

---

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t lexora-ai -f docker/Dockerfile .

# Run container
docker run -d \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  -e OPENAI_API_KEY="sk-..." \
  -p 8000:8000 \
  lexora-ai
```

### Docker Compose

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Cloud Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions on:

- AWS ECS deployment
- GCP Cloud Run deployment
- Kubernetes deployment
- Terraform infrastructure

---

## Security

### Authentication

- JWT tokens with short-lived access tokens
- Refresh tokens for session extension
- Password hashing with bcrypt
- Rate limiting on authentication endpoints

### Authorization

- User-level data isolation
- Document-level access control
- Role-based permissions (admin/user)

### Data Protection

- HTTPS/TLS in transit
- Environment variable secrets
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)

### Security Best Practices

```python
# Always validate file uploads
ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Implement rate limiting
from fastapi_limiter import Limiter
limiter = Limiter(key_func=get_remote_address)

# Use parameterized queries (automatic with SQLAlchemy)
# Never concatenate user input into SQL
```

---

## Monitoring

### Metrics

Prometheus metrics are exposed at `/metrics`:

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/chat",status="200"}

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="POST",endpoint="/api/v1/documents",le="0.1"}
```

### Logging

Structured JSON logging with correlation IDs:

```json
{
  "event": "document_uploaded",
  "user_id": "user-123",
  "document_id": "doc-456",
  "filename": "report.pdf",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Health Checks

- `/health` - Basic liveness check
- `/ready` - Readiness check (database + Redis)

---

## Scaling

### Scaling to 10k+ Users

1. **Horizontal Scaling**
   - Deploy multiple API instances behind load balancer
   - Use sticky sessions or JWT for stateless auth

2. **Database Scaling**
   - Add read replicas for read-heavy workloads
   - Implement connection pooling (PgBouncer)

3. **Vector Database**
   - Migrate from FAISS to Pinecone/Weaviate
   - Use sharding for large datasets

4. **Caching**
   - Redis Cluster for high availability
   - Cache embeddings and frequent queries

5. **Async Processing**
   - Scale Celery workers based on queue depth
   - Use priority queues for urgent tasks

### Performance Tuning

```python
# Database
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10

# Embeddings
EMBEDDING_BATCH_SIZE = 100

# Caching
CACHE_TTL = 3600  # 1 hour for embeddings
QUERY_CACHE_TTL = 300  # 5 minutes for queries
```

---

## Contributing

### Bug Reports

Please use GitHub Issues to report bugs. Include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details

### Feature Requests

Open an issue with:

- Feature description
- Use case
- Proposed implementation (optional)

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure CI passes
5. Submit PR with description

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [LangChain](https://langchain.com/) - LLM orchestration
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [OpenAI](https://openai.com/) - LLM and embeddings

---

## Support

- Documentation: https://docs.lexora.ai
- Discord: https://discord.gg/lexora
- Email: support@lexora.ai

---

<p align="center">Built with ❤️ by the Lexora Team</p>
