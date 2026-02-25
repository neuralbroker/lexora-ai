# Lexora AI - Enterprise Knowledge Intelligence Platform

<p align="center">
  <img src="https://via.placeholder.com/200x200?text=Lexora+AI" alt="Lexora AI Logo" />
</p>

<p align="center">
  <strong>Enterprise Knowledge Intelligence Platform</strong><br />
  Build AI-powered document question-answering systems with production-grade architecture
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python 3.11+" />
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-0.109+-00a393.svg" alt="FastAPI" />
  </a>
  <a href="https://github.com/sajadkoder/lexora-ai/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT" />
  </a>
  <a href="https://github.com/sajadkoder/lexora-ai/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/sajadkoder/lexora-ai/ci.yml" alt="CI" />
  </a>
  <a href="https://github.com/sajadkoder/lexora-ai/stargazers">
    <img src="https://img.shields.io/github/stars/sajadkoder/lexora-ai" alt="Stars" />
  </a>
  <a href="https://github.com/sajadkoder/lexora-ai/forks">
    <img src="https://img.shields.io/github/forks/sajadkoder/lexora-ai" alt="Forks" />
  </a>
</p>

---

## Table of Contents

1. [Introduction](#introduction)
2. [Why Lexora AI?](#why-lexora-ai)
3. [System Architecture](#system-architecture)
   - [High-Level Design](#high-level-design)
   - [Component Diagram](#component-diagram)
   - [Data Flow](#data-flow)
   - [Technology Stack](#technology-stack)
4. [Features](#features)
   - [Core Features](#core-features)
   - [Technical Features](#technical-features)
   - [API Endpoints](#api-endpoints)
5. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Quick Start Guide](#quick-start-guide)
   - [Environment Configuration](#environment-configuration)
6. [Project Structure](#project-structure)
   - [Directory Layout](#directory-layout)
   - [Key Files Explained](#key-files-explained)
7. [Database Design](#database-design)
   - [Schema Overview](#schema-overview)
   - [Entity Relationships](#entity-relationships)
8. [API Documentation](#api-documentation)
   - [Authentication](#authentication)
   - [Documents](#documents)
   - [Chat](#chat)
   - [Health Checks](#health-checks)
9. [Configuration](#configuration)
   - [Environment Variables](#environment-variables)
   - [Configuration Options](#configuration-options)
10. [Development Guide](#development-guide)
    - [Local Development](#local-development)
    - [Running Tests](#running-tests)
    - [Code Quality](#code-quality)
    - [Adding New Features](#adding-new-features)
11. [Deployment](#deployment)
    - [Docker Deployment](#docker-deployment)
    - [Docker Compose](#docker-compose)
    - [Production Considerations](#production-considerations)
12. [Cloud Deployment](#cloud-deployment)
    - [AWS ECS](#aws-ecs)
    - [GCP Cloud Run](#gcp-cloud-run)
    - [Kubernetes](#kubernetes)
13. [Security](#security)
    - [Authentication & Authorization](#authentication--authorization)
    - [Data Protection](#data-protection)
    - [Security Best Practices](#security-best-practices)
14. [Monitoring & Observability](#monitoring--observability)
    - [Metrics](#metrics)
    - [Logging](#logging)
    - [Health Checks](#health-checks-1)
    - [Alerting](#alerting)
15. [Scaling Guide](#scaling-guide)
    - [Scaling to 10k Users](#scaling-to-10k-users)
    - [Performance Tuning](#performance-tuning)
    - [Optimization Strategies](#optimization-strategies)
16. [Advanced Topics](#advanced-topics)
    - [RAG Pipeline Deep Dive](#rag-pipeline-deep-dive)
    - [Text Chunking Strategy](#text-chunking-strategy)
    - [Embedding Generation](#embedding-generation)
    - [Vector Storage](#vector-storage)
17. [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [FAQ](#faq)
18. [Roadmap](#roadmap)
19. [Contributing](#contributing)
20. [License](#license)
21. [Acknowledgments](#acknowledgments)
22. [Support](#support)

---

## Introduction

Lexora AI is an enterprise-grade knowledge intelligence platform that enables organizations to harness the power of their documents through artificial intelligence. Built with modern best practices and production-grade architecture, it provides a scalable solution for building document question-answering systems.

### What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that enhances Large Language Model (LLM) responses by retrieving relevant information from a knowledge base and using it as context for generating answers. This approach offers several advantages:

- **Accuracy**: Responses are grounded in actual document content
- **Attribution**: Sources are cited, allowing users to verify information
- **Freshness**: Knowledge can be updated without retraining the model
- **Cost-effectiveness**: Reduces token usage by retrieving only relevant content
- **Privacy**: Sensitive data stays within your infrastructure

---

## Why Lexora AI?

Lexora AI stands out as a production-ready solution for several key reasons:

### 1. Enterprise-Ready Architecture

- **Clean separation of concerns**: Business logic is completely isolated from API layer
- **Dependency injection**: All dependencies are explicitly declared and testable
- **Comprehensive error handling**: Custom exception hierarchy with proper HTTP status codes
- **Structured logging**: JSON logging with correlation IDs for easy troubleshooting

### 2. Production-Grade Code Quality

- **Type hints throughout**: Full type annotations for better IDE support and documentation
- **Async/await throughout**: Non-blocking I/O for maximum throughput
- **Connection pooling**: Optimized database and Redis connections
- **Graceful shutdowns**: Proper cleanup of resources on application termination

### 3. Scalable Design

- **Horizontal scaling**: Stateless design allows easy scaling
- **Async processing**: Heavy tasks are offloaded to background workers
- **Caching layer**: Redis caching reduces redundant computations
- **Vector database**: FAISS provides efficient similarity search

### 4. Developer Experience

- **Comprehensive API docs**: Auto-generated OpenAPI documentation
- **Testing infrastructure**: Pytest with fixtures and mocks
- **Code formatting**: Black and isort for consistent style
- **Type checking**: Mypy for catching type errors early

---

## System Architecture

### High-Level Design

Lexora AI follows a microservices-inspired architecture with clear boundaries between components:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              LEXORA AI ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          CLIENT LAYER                                   │   │
│  │   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐          │   │
│  │   │  React   │   │  Mobile  │   │   API    │   │   CLI    │          │   │
│  │   │   Web    │   │    App   │   │ Clients  │   │   Tool   │          │   │
│  │   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘          │   │
│  └────────┼──────────────┼──────────────┼──────────────┼─────────────────┘   │
│           │              │              │              │                      │
│           └──────────────┴──────────────┴──────────────┘                      │
│                                      │                                         │
│                                      ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         LOAD BALANCER / API GATEWAY                      │   │
│  │              (Authentication, Rate Limiting, SSL Termination)           │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                            │
│           ┌───────────────────────┼───────────────────────┐                  │
│           │                       │                       │                  │
│           ▼                       ▼                       ▼                  │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐               │
│  │  FastAPI App   │    │     Celery     │    │  Prometheus   │               │
│  │   (Primary)    │    │    Workers     │    │   Exporter    │               │
│  │   Port 8000   │    │  (Async Tasks) │    │   (Metrics)   │               │
│  └───────┬────────┘    └───────┬────────┘    └────────────────┘               │
│          │                     │                                            │
│          │                     │ (Task Queue)                                │
│          │                     ▼                                            │
│          │            ┌────────────────┐                                      │
│          │            │     Redis      │                                      │
│          │            │  (Broker +     │                                      │
│          │            │   Cache)       │                                      │
│          │            └───────┬────────┘                                      │
│          │                    │                                              │
│          ▼                    │                                              │
│  ┌────────────────┐          │                                              │
│  │  PostgreSQL    │          │                                              │
│  │  (Metadata &   │          │                                              │
│  │   Chat History)│          │                                              │
│  └───────┬────────┘          │                                              │
│          │                   │                                              │
│          │                   ▼                                              │
│          │          ┌────────────────┐                                       │
│          │          │ FAISS Vector  │                                       │
│          └─────────▶│     Store     │◀──────────────┘                      │
│                     └────────────────┘                                      │
│                                                                              │
│                     ┌────────────────┐                                       │
│                     │   S3/Local    │                                       │
│                     │   Storage     │                                       │
│                     │  (Documents)  │                                       │
│                     └────────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
                           ┌──────────────────────────────────────┐
                           │           CLIENT REQUESTS            │
                           └──────────────────┬───────────────────┘
                                              │
                                              ▼
                           ┌──────────────────────────────────────┐
                           │       FASTAPI APPLICATION            │
                           │  ┌────────────────────────────────┐  │
                           │  │     Authentication Middleware   │  │
                           │  └────────────────────────────────┘  │
                           │  ┌────────────────────────────────┐  │
                           │  │    Rate Limiting Middleware    │  │
                           │  └────────────────────────────────┘  │
                           │  ┌────────────────────────────────┐  │
                           │  │     Request/Response Logging   │  │
                           │  └────────────────────────────────┘  │
                           └──────────────────┬───────────────────┘
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      │                       │                       │
                      ▼                       ▼                       ▼
          ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
          │   AUTH ROUTER     │  │  DOCUMENTS ROUTER │  │    CHAT ROUTER    │
          │                   │  │                   │  │                   │
          │ • /register       │  │ • /documents     │  │ • /conversations │
          │ • /login          │  │ • /documents/{id}│  │ • /message        │
          │ • /refresh        │  │ • /documents/{id}│  │ • /stream         │
          │ • /logout         │  │   /status       │  │                   │
          │ • /me             │  │ • POST upload   │  │                   │
          └─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
                    │                       │                       │
                    └───────────────────────┼───────────────────────┘
                                            │
                                            ▼
          ┌────────────────────────────────────────────────────────────────┐
          │                      SERVICE LAYER                             │
          │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
          │  │ Auth Service │  │ Doc Service  │  │ Chat Service │        │
          │  └──────────────┘  └──────────────┘  └──────────────┘        │
          │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
          │  │ Embedding    │  │   Vector     │  │  Retrieval   │        │
          │  │  Service     │  │   Service    │  │  Service     │        │
          │  └──────────────┘  └──────────────┘  └──────────────┘        │
          │  ┌──────────────┐  ┌──────────────┐                          │
          │  │    LLM       │  │   Cache      │                          │
          │  │  Service     │  │  Service     │                          │
          │  └──────────────┘  └──────────────┘                          │
          └────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
          ┌────────────────────────────────────────────────────────────────┐
          │                      DATA LAYER                               │
          │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
          │  │  PostgreSQL  │  │    FAISS     │  │    Redis     │        │
          │  │              │  │              │  │              │        │
          │  │ • Users      │  │ • Embeddings │  │ • Cache      │        │
          │  │ • Documents  │  │ • Search     │  │ • Queue      │        │
          │  │ • Messages   │  │              │  │ • Sessions   │        │
          │  │ • Sessions   │  │              │  │              │        │
          │  └──────────────┘  └──────────────┘  └──────────────┘        │
          └────────────────────────────────────────────────────────────────┘
```

### Data Flow

The complete data flow for document processing and querying:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DOCUMENT UPLOAD FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. UPLOAD PHASE                                                               │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  Client  │────▶│  FastAPI     │────▶│   Save to    │────▶│   Create    │ │
│  │ Request │     │  Endpoint    │     │   Disk/S3    │     │   DB Record │ │
│  └──────────┘     └──────────────┘     └──────────────┘     └──────────────┘ │
│                                                                                 │
│  2. PROCESSING PHASE (Async)                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Celery      │────▶│    Extract   │────▶│    Chunk     │                 │
│  │   Worker      │     │    Text       │     │    Text      │                 │
│  └──────────────┘     └──────────────┘     └──────┬───────┘                 │
│                                                      │                         │
│                                                      ▼                         │
│  3. EMBEDDING PHASE                                  │                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   OpenAI     │◀────│  Embedding   │────▶│   Generate   │                 │
│  │   API        │     │   Service    │     │   Vectors    │                 │
│  └──────────────┘     └──────────────┘     └──────┬───────┘                 │
│                                                     │                         │
│                                                     ▼                         │
│  4. STORAGE PHASE                                                         │                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   FAISS      │◀────│   Vector     │────▶│    Store     │                 │
│  │   Index      │     │   Service    │     │   Vectors    │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           QUERY/RESPONSE FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. QUERY PHASE                                                               │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐                      │
│  │  Client  │────▶│  FastAPI     │────▶│   Embed      │                      │
│  │  Query   │     │  Chat API    │     │   Query      │                      │
│  └──────────┘     └──────────────┘     └──────┬───────┘                      │
│                                                  │                              │
│                                                  ▼                              │
│  2. RETRIEVAL PHASE                                                        │                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   FAISS      │◀────│   Vector     │────▶│   Search     │                 │
│  │   Index      │     │   Service    │     │   Similar    │                 │
│  └──────────────┘     └──────────────┘     └──────┬───────┘                 │
│                                                     │                         │
│                                                     ▼                         │
│  3. GENERATION PHASE                                                        │                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   OpenAI     │◀────│    LLM       │────▶│    Build     │                 │
│  │   GPT-4      │     │   Service    │     │   Prompt     │                 │
│  └──────────────┘     └──────────────┘     └──────┬───────┘                 │
│                                                     │                         │
│                                                     ▼                         │
│  4. RESPONSE PHASE                                                         │                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Client     │◀────│   SSE        │────▶│   Stream     │                 │
│  │  (Browser)   │     │   Response   │     │   Response   │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Language** | Python | 3.11+ | Core programming language |
| **Web Framework** | FastAPI | 0.109+ | REST API framework |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Database Driver** | asyncpg | 0.29+ | Async PostgreSQL driver |
| **Validation** | Pydantic | 2.5+ | Data validation |
| **AI/LLM** | LangChain | 0.1+ | RAG orchestration |
| **LLM Provider** | OpenAI | 1.10+ | GPT models |
| **Embeddings** | OpenAI Embeddings | - | Text vectorization |
| **Vector Database** | FAISS | 1.7+ | Similarity search |
| **Cache** | Redis | 7+ | Caching & message queue |
| **Task Queue** | Celery | 5.3+ | Async task processing |
| **Authentication** | python-jose | 3.3+ | JWT handling |
| **Password Hashing** | passlib/bcrypt | 4.1+ | Secure password storage |
| **Logging** | structlog | 24.1+ | Structured logging |
| **Monitoring** | prometheus-client | 0.19+ | Metrics collection |
| **Container** | Docker | 24+ | Application packaging |
| **Document Parsing** | pypdf, python-docx | Latest | File text extraction |

---

## Features

### Core Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Document Upload** | Support for PDF, TXT, MD, DOCX files | FastAPI multipart upload with validation |
| **Text Extraction** | Intelligent text extraction | pypdf for PDFs, python-docx for Word |
| **Smart Chunking** | Semantic text splitting with overlap | Custom TextChunker with configurable size |
| **Vector Embeddings** | OpenAI text-embedding-3-small | LangChain OpenAIEmbeddings |
| **RAG Pipeline** | Retrieval-augmented generation | LangChain ConversationalRetrievalChain |
| **Streaming Responses** | Real-time token streaming | Server-Sent Events (SSE) |
| **Chat History** | Persistent conversation storage | PostgreSQL with SQLAlchemy |
| **JWT Authentication** | Secure token-based auth | python-jose with access/refresh tokens |
| **User Isolation** | Per-user data separation | UUID-based user partitioning |

### Technical Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Async Processing** | Non-blocking document handling | Celery with Redis broker |
| **Caching** | Redis caching for embeddings | Custom CacheService |
| **Structured Logging** | JSON logs with correlation IDs | structlog with context |
| **Health Checks** | Liveness and readiness probes | FastAPI health endpoints |
| **Metrics** | Prometheus metrics export | prometheus-client |
| **Error Handling** | Custom exception hierarchy | LexoraException classes |
| **Rate Limiting** | Configurable rate limits | Middleware (extensible) |
| **Connection Pooling** | Optimized DB/Redis connections | SQLAlchemy & Redis pooling |

### API Endpoints

#### Authentication Endpoints

```
POST   /api/v1/auth/register          - Register new user account
POST   /api/v1/auth/login            - Login and get JWT tokens
POST   /api/v1/auth/refresh          - Refresh access token
POST   /api/v1/auth/logout           - Invalidate session
GET    /api/v1/auth/me              - Get current user profile
```

#### Document Endpoints

```
GET    /api/v1/documents             - List user's uploaded documents
POST   /api/v1/documents             - Upload new document (multipart/form-data)
GET    /api/v1/documents/{id}        - Get document details and metadata
GET    /api/v1/documents/{id}/status - Get document processing status
DELETE /api/v1/documents/{id}        - Delete document and vectors
```

#### Chat Endpoints

```
GET    /api/v1/chat/conversations    - List all conversations
POST   /api/v1/chat/conversations    - Create new conversation
GET    /api/v1/chat/conversations/{id} - Get conversation messages
DELETE /api/v1/chat/conversations/{id} - Delete conversation
POST   /api/v1/chat/message          - Send message (non-streaming response)
POST   /api/v1/chat/stream           - Send message (streaming SSE response)
```

#### System Endpoints

```
GET    /health                        - Basic liveness check
GET    /ready                         - Readiness check (DB + Redis)
GET    /metrics                       - Prometheus metrics endpoint
GET    /                              - Root endpoint with API info
```

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Installation |
|-------------|---------|--------------|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **Docker** | 24+ | [docker.com](https://www.docker.com/get-started/) |
| **Docker Compose** | 2.0+ | Included with Docker Desktop |
| **PostgreSQL** | 15+ | Via Docker or [postgresql.org](https://www.postgresql.org/download/) |
| **Redis** | 7+ | Via Docker or [redis.io](https://redis.io/download/) |
| **Git** | 2.0+ | [git-scm.com](https://git-scm.com/) |

### Quick Start Guide

This guide will get you up and running with Lexora AI in under 5 minutes.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/sajadkoder/lexora-ai.git
cd lexora-ai
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor and configure:
# - DATABASE_URL (PostgreSQL connection string)
# - REDIS_URL (Redis connection string)
# - SECRET_KEY (Generate a secure key)
# - OPENAI_API_KEY (Your OpenAI API key)
```

#### Step 5: Start Infrastructure Services

```bash
# Using Docker Compose (recommended)
cd docker
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### Step 6: Initialize Database

```bash
# The database tables will be created automatically on first run
# Or run migrations manually:
alembic upgrade head
```

#### Step 7: Start the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or run directly
python -m app.main
```

#### Step 8: Access the API

Open your browser and navigate to:

| Endpoint | Description |
|----------|-------------|
| [http://localhost:8000](http://localhost:8000) | API root |
| [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI |
| [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc documentation |
| [http://localhost:8000/health](http://localhost:8000/health) | Health check |

### Environment Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

```bash
# Application
APP_NAME=Lexora AI
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lexora
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=pdf,txt,md,docx

# Vector Storage
FAISS_INDEX_PATH=./data/faiss
EMBEDDING_BATCH_SIZE=100

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Project Structure

### Directory Layout

```
lexora-ai/
├── app/                           # Main application package
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management (Pydantic)
│   ├── deps.py                   # Dependency injection helpers
│   │
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   ├── v1/                  # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── router.py        # Main API router
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── documents.py    # Document endpoints
│   │   │   └── chat.py          # Chat endpoints
│   │   └── dependencies.py     # API-level dependencies
│   │
│   ├── core/                    # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py          # JWT, password hashing
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging.py          # Logging configuration
│   │
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   └── user.py             # Request/response models
│   │
│   ├── schemas/                 # Database models
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy models
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── document_service.py   # Document processing
│   │   ├── embedding_service.py  # OpenAI embeddings
│   │   ├── vector_service.py     # FAISS operations
│   │   ├── retrieval_service.py  # Context retrieval
│   │   ├── llm_service.py       # LLM integration
│   │   ├── chat_service.py      # Chat orchestration
│   │   └── cache_service.py     # Redis caching
│   │
│   ├── tasks/                   # Background tasks
│   │   ├── __init__.py
│   │   ├── document_processor.py # Celery tasks
│   │   └── worker.py            # Celery worker config
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── text_chunker.py       # Text splitting
│       ├── document_parser.py    # File parsing
│       └── helpers.py           # General helpers
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_text_chunker.py
│   │   └── test_services.py
│   └── integration/             # Integration tests
│       ├── __init__.py
│       └── test_api.py
│
├── docker/                     # Docker configuration
│   ├── Dockerfile              # Application image
│   ├── Dockerfile.worker       # Celery worker image
│   └── docker-compose.yml      # Local development
│
├── scripts/                    # Utility scripts
│   ├── init_db.py             # Database initialization
│   └── seed_data.py           # Seed test data
│
├── alembic/                    # Database migrations
│   └── versions/              # Migration files
│
├── .env.example               # Environment template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── pyproject.toml            # Project configuration
├── pytest.ini               # Pytest configuration
├── alembic.ini             # Alembic configuration
├── DEPLOYMENT.md           # Deployment guide
└── README.md               # This file
```

### Key Files Explained

#### `app/main.py`
The FastAPI application entry point. Sets up:
- CORS middleware
- Exception handlers
- Prometheus metrics middleware
- API routers
- Health check endpoints
- Lifespan management (startup/shutdown)

#### `app/config.py`
Configuration management using Pydantic Settings:
- Environment variable loading
- Validation with defaults
- Computed properties (e.g., `is_production`)

#### `app/deps.py`
Dependency injection helpers:
- `get_db()`: Database session
- `get_current_user()`: JWT authentication
- `require_admin()`: Admin authorization

#### `app/api/v1/`
REST API endpoints organized by domain:
- **auth.py**: Registration, login, token refresh
- **documents.py**: Upload, list, delete documents
- **chat.py**: Conversations, messaging, streaming

#### `app/services/`
Business logic layer:
- **document_service.py**: Orchestrates document processing
- **embedding_service.py**: OpenAI embeddings
- **vector_service.py**: FAISS index management
- **retrieval_service.py**: Semantic search
- **llm_service.py**: GPT-4 integration
- **chat_service.py**: Conversation handling
- **cache_service.py**: Redis caching

#### `app/schemas/database.py`
SQLAlchemy ORM models:
- User, Document, Conversation, Message, APIKey

---

## Database Design

### Schema Overview

The database uses a relational model with the following entities:

```
┌──────────────────┐       ┌──────────────────┐
│      users       │       │     documents    │
├──────────────────┤       ├──────────────────┤
│ id (PK)          │       │ id (PK)          │
│ email (UNIQUE)   │       │ user_id (FK)     │
│ password_hash    │──────▶│ filename         │
│ full_name        │       │ file_path        │
│ is_active        │       │ file_type        │
│ is_admin         │       │ file_size        │
│ created_at       │       │ status           │
│ updated_at       │       │ chunk_count      │
└──────────────────┘       │ vector_ids       │
                           │ created_at       │
                           │ updated_at       │
                           └──────────────────┘
                                    │
                                    │ user_id
                                    ▼
┌──────────────────┐       ┌──────────────────┐
│     messages     │       │  conversations   │
├──────────────────┤       ├──────────────────┤
│ id (PK)          │       │ id (PK)          │
│ conversation_id  │──────▶│ user_id (FK)     │
│ user_id (FK)     │       │ title            │
│ role             │       │ created_at       │
│ content          │       │ updated_at       │
│ sources (JSON)   │       └──────────────────┘
│ created_at       │
└──────────────────┘
```

### Entity Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Documents | One-to-Many | A user can upload multiple documents |
| User → Conversations | One-to-Many | A user can have multiple conversations |
| Conversation → Messages | One-to-Many | A conversation has multiple messages |
| Message → User | Many-to-One | Each message belongs to a user |
| User → API Keys | One-to-Many | A user can have multiple API keys |

---

## API Documentation

### Authentication

#### Register New User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com
password=securepassword123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Upload Document

```http
POST /api/v1/documents
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary>
```

**Response** (201 Created):
```json
{
  "id": "uuid-string",
  "filename": "document.pdf",
  "status": "processing",
  "message": "Document uploaded successfully. Processing in background.",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Send Chat Message (Streaming)

```http
POST /api/v1/chat/stream
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "What is this document about?",
  "conversation_id": "uuid-string (optional)",
  "document_ids": ["uuid-string"] (optional)
}
```

**Response** (200 OK):
```
data: {"type": "chunk", "content": "This", "conversation_id": "..."}
data: {"type": "chunk", "content": " document", "conversation_id": "..."}
data: {"type": "chunk", "content": " discusses", "conversation_id": "..."}
data: {"type": "done", "conversation_id": "..."}
```

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| **Application** | | | | |
| `APP_NAME` | Application name | No | Lexora AI | Lexora AI |
| `ENVIRONMENT` | Environment name | No | development | production |
| `DEBUG` | Enable debug mode | No | false | true |
| **Server** | | | | |
| `HOST` | Server host | No | 0.0.0.0 | 0.0.0.0 |
| `PORT` | Server port | No | 8000 | 8000 |
| **Database** | | | | |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - | postgresql+asyncpg://user:pass@localhost:5432/db |
| `DATABASE_POOL_SIZE` | Connection pool size | No | 20 | 20 |
| `DATABASE_MAX_OVERFLOW` | Max overflow connections | No | 10 | 10 |
| `DATABASE_ECHO` | Log SQL queries | No | false | false |
| **Redis** | | | | |
| `REDIS_URL` | Redis connection string | Yes | - | redis://localhost:6379/0 |
| **Authentication** | | | | |
| `SECRET_KEY` | JWT signing key | Yes | - | min-32-char-secret-key |
| `ALGORITHM` | JWT algorithm | No | HS256 | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | No | 30 | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | No | 7 | 7 |
| **OpenAI** | | | | |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - | sk-... |
| `OPENAI_MODEL` | GPT model | No | gpt-4-turbo-preview | gpt-4-turbo-preview |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | No | text-embedding-3-small | text-embedding-3-small |
| `OPENAI_EMBEDDING_DIMENSIONS` | Embedding dimensions | No | 1536 | 1536 |
| `OPENAI_MAX_TOKENS` | Max response tokens | No | 2000 | 2000 |
| `OPENAI_TEMPERATURE` | Response creativity | No | 0.7 | 0.7 |
| **Storage** | | | | |
| `UPLOAD_DIR` | Upload directory | No | ./uploads | ./uploads |
| `MAX_FILE_SIZE` | Max file size (bytes) | No | 52428800 | 52428800 |
| `ALLOWED_EXTENSIONS` | Allowed file types | No | pdf,txt,md,docx | pdf,txt,md,docx |
| **Vector Store** | | | | |
| `FAISS_INDEX_PATH` | FAISS index directory | No | ./data/faiss | ./data/faiss |
| `EMBEDDING_BATCH_SIZE` | Batch size for embeddings | No | 100 | 100 |
| **Celery** | | | | |
| `CELERY_BROKER_URL` | Celery broker URL | Yes | - | redis://localhost:6379/1 |
| `CELERY_RESULT_BACKEND` | Celery result backend | Yes | - | redis://localhost:6379/2 |
| **Logging** | | | | |
| `LOG_LEVEL` | Log level | No | INFO | INFO |
| `LOG_FORMAT` | Log format | No | json | json |
| `SENTRY_DSN` | Sentry DSN | No | - | https://...@sentry.io/... |

---

## Development Guide

### Local Development

#### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run with multiple workers
uvicorn app.main:app --workers 4

# Run with debug mode
uvicorn app.main:app --reload --log-level debug
```

#### Running Background Workers

```bash
# Start Celery worker
celery -A app.tasks.worker worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.tasks.worker beat --loglevel=info
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_auth.py

# Run specific test
pytest tests/unit/test_auth.py::test_register_success

# Run tests in watch mode
pytest --watch

# Run with verbose output
pytest -vv

# Run tests matching pattern
pytest -k "test_auth"
```

### Code Quality

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check types with mypy
mypy .

# Lint with flake8
flake8 .

# Run all checks
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
```

### Adding New Features

1. **Create a service** in `app/services/`:
   ```python
   class NewService:
       def __init__(self, db: AsyncSession, user: User):
           self.db = db
           self.user = user
       
       async def do_something(self) -> Result:
           # Implementation
           pass
   ```

2. **Add Pydantic models** in `app/models/`:
   ```python
   class NewRequest(BaseModel):
       field: str
   
   class NewResponse(BaseModel):
       result: str
   ```

3. **Create API endpoints** in `app/api/v1/`:
   ```python
   @router.post("/new", response_model=NewResponse)
   async def create_new(
       request: NewRequest,
       db: DBSession,
       current_user: CurrentUser,
   ) -> NewResponse:
       service = NewService(db, current_user)
       result = await service.do_something()
       return result
   ```

4. **Add tests** in `tests/`:
   ```python
   @pytest.mark.asyncio
   async def test_new_feature(client: AsyncClient, auth_headers):
       response = await client.post("/api/v1/new", headers=auth_headers, json={})
       assert response.status_code == 200
   ```

---

## Deployment

### Docker Deployment

#### Building the Image

```bash
# Build the production image
docker build -t lexora-ai:latest -f docker/Dockerfile .

# Tag for registry
docker tag lexora-ai:latest registry.example.com/lexora-ai:v1.0.0
docker tag lexora-ai:latest registry.example.com/lexora-ai:latest

# Push to registry
docker push registry.example.com/lexora-ai:v1.0.0
```

#### Running the Container

```bash
docker run -d \
  --name lexora-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://postgres:password@db:5432/lexora" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e SECRET_KEY="your-secret-key" \
  -e OPENAI_API_KEY="sk-..." \
  lexora-ai:latest
```

### Docker Compose

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f app

# Scale the application
docker-compose -f docker/docker-compose.yml up -d --scale app=3

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Production Considerations

1. **Use a reverse proxy** (nginx, Traefik)
2. **Enable HTTPS/TLS**
3. **Use secrets management** (AWS Secrets Manager, GCP Secret Manager)
4. **Configure logging** to external service (CloudWatch, Stackdriver)
5. **Set up monitoring** (DataDog, New Relic)
6. **Use load balancing**
7. **Configure health checks**

---

## Cloud Deployment

### AWS ECS

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed AWS ECS deployment instructions including:
- ECS cluster setup
- Task definitions
- Load balancer configuration
- Auto-scaling
- CI/CD with CodePipeline

### GCP Cloud Run

```bash
# Build and push image
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT/lexora/lexora

# Deploy
gcloud run deploy lexora \
  --image us-central1-docker.pkg.dev/$PROJECT/lexora/lexora \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="...",REDIS_URL="..."
```

### Kubernetes

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lexora-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lexora-api
  template:
    metadata:
      labels:
        app: lexora-api
    spec:
      containers:
      - name: api
        image: lexora:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: lexora-secrets
              key: database-url
```

---

## Security

### Authentication & Authorization

- **JWT tokens**: Short-lived access tokens (30 min) with refresh tokens (7 days)
- **Password hashing**: bcrypt with salt
- **User isolation**: All queries filtered by user_id
- **Role-based access**: Admin and user roles

### Data Protection

- **Encryption in transit**: HTTPS/TLS
- **Secrets management**: Environment variables or secret managers
- **Input validation**: Pydantic models
- **SQL injection prevention**: SQLAlchemy ORM
- **File upload validation**: Type and size limits

### Security Best Practices

```python
# Password requirements
MIN_PASSWORD_LENGTH = 8

# File validation
ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Rate limiting (implement in middleware)
RATE_LIMIT_PER_MINUTE = 60
```

---

## Monitoring & Observability

### Metrics

Prometheus metrics available at `/metrics`:

```prometheus
# Request metrics
http_requests_total{method="GET",endpoint="/api/v1/chat",status="200"}
http_request_duration_seconds_bucket{method="POST",endpoint="/api/v1/documents",le="0.5"}

# Custom metrics
document_processing_duration_seconds
llm_token_usage_total
cache_hit_total
cache_miss_total
```

### Logging

Structured JSON logging:
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "event": "document_uploaded",
  "user_id": "user-123",
  "document_id": "doc-456",
  "filename": "report.pdf",
  "file_size": 1048576
}
```

### Health Checks

| Endpoint | Purpose | Checks |
|----------|---------|--------|
| `/health` | Liveness | Application running |
| `/ready` | Readiness | Database + Redis connected |

### Alerting

Recommended alerts:
- Error rate > 5%
- Latency p95 > 2 seconds
- Database connections > 80%
- Redis memory > 80%
- Queue depth growing

---

## Scaling Guide

### Scaling to 10k Users

1. **Horizontal scaling**: Deploy multiple API instances behind load balancer
2. **Database read replicas**: Add read replicas for PostgreSQL
3. **Vector database migration**: FAISS → Pinecone/Weaviate
4. **Redis clustering**: Redis Cluster for high availability
5. **CDN**: CloudFront for static assets
6. **Async workers**: Scale Celery workers based on queue depth

### Performance Tuning

```python
# Database
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10

# Embeddings
EMBEDDING_BATCH_SIZE = 100

# Caching
CACHE_TTL = 3600  # 1 hour
QUERY_CACHE_TTL = 300  # 5 minutes

# Vector search
RETRIEVAL_K = 4  # Number of results to retrieve
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Database connection error | Check DATABASE_URL, ensure PostgreSQL is running |
| Redis connection error | Check REDIS_URL, ensure Redis is running |
| OpenAI API error | Verify OPENAI_API_KEY is valid |
| File upload fails | Check file size and allowed extensions |
| Slow queries | Enable caching, check FAISS index |

### FAQ

**Q: How do I reset my password?**
A: Currently not implemented. Contact admin to reset.

**Q: Can I use my own LLM?**
A: Yes, modify `app/services/llm_service.py` to use a different provider.

**Q: How do I add more document types?**
A: Add parsers in `app/utils/document_parser.py`.

---

## Roadmap

- [ ] Multi-language support
- [ ] Admin dashboard
- [ ] Webhooks for events
- [ ] API versioning
- [ ] Advanced analytics
- [ ] Multi-tenant support

---

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [LangChain](https://langchain.com/) - LLM application framework
- [FAISS](https://github.com/facebookresearch/faiss) - Efficient similarity search
- [OpenAI](https://openai.com/) - GPT models and embeddings
- [PostgreSQL](https://www.postgresql.org/) - Reliable database
- [Redis](https://redis.io/) - In-memory data store

---

## Support

- 📧 Email: sajad@lexora.ai
- 🐛 Issues: [github.com/sajadkoder/lexora-ai/issues](https://github.com/sajadkoder/lexora-ai/issues)
- 💻 GitHub: [github.com/sajadkoder](https://github.com/sajadkoder)

---

<p align="center">
  <strong>Built with ❤️ by Sajad</strong><br />
  <sub>Empowering enterprises with intelligent document search</sub>
</p>
