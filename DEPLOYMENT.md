# Lexora AI - Deployment Guide

## Prerequisites

- Docker & Docker Compose
- AWS/GCP account
- OpenAI API key

## Local Development

```bash
# Clone the repository
git clone https://github.com/your-org/lexora-ai.git
cd lexora-ai

# Copy environment variables
cp .env.example .env

# Start services
docker-compose -f docker/docker-compose.yml up -d

# Run database migrations
docker-compose exec app alembic upgrade head

# Access the application
open http://localhost:8000/docs
```

## AWS Deployment

### Infrastructure Setup (Terraform)

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# ECS Cluster
resource "aws_ecs_cluster" "lexora" {
  name = "lexora-cluster"
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier           = "lexora-postgres"
  engine              = "postgres"
  engine_version      = "15.3"
  instance_class      = "db.t3.medium"
  allocated_storage   = 20
  db_name             = "lexora"
  username            = "postgres"
  password            = var.db_password
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "lexora-redis"
  engine              = "redis"
  node_type           = "cache.t3.micro"
  num_cache_nodes     = 1
  parameter_group_name = "default.redis7"
}

# ECR Repository
resource "aws_ecr_repository" "lexora" {
  name = "lexora-app"
}
```

### ECS Task Definition

```json
{
  "family": "lexora",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/lexora:latest",
      "essential": true,
      "portMappings": [
        {"containerPort": 8000, "protocol": "tcp"}
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql+asyncpg://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/lexora",
          "awslogs-region": "us-east-1"
        }
      }
    }
  ]
}
```

### Deployment Commands

```bash
# Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker build -t lexora -f docker/Dockerfile .
docker tag lexora:latest your-account.dkr.ecr.us-east-1.amazonaws.com/lexora:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/lexora:latest

# Update ECS service
aws ecs update-service --cluster lexora-cluster --service lexora --force-new-deployment
```

## GCP Deployment

### Infrastructure Setup

```bash
# Enable services
gcloud services enable compute.googleapis.com container.googleapis.com cloudrun.googleapis.com

# Create Cloud SQL instance
gcloud sql instances create lexora-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-us1

# Create Redis instance
gcloud redis instances create lexora-redis --zone=us-central1-a --tier=basic

# Create Artifact Registry
gcloud artifacts repositories create lexora --repository-type=docker --location=us-central1
```

### Cloud Run Deployment

```bash
# Build and deploy
gcloud builds submit --tag us-central1-docker.pkg.dev/your-project/lexora/lexora

gcloud run deploy lexora \
    --image us-central1-docker.pkg.dev/your-project/lexora/lexora \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL="postgresql+asyncpg://...",REDIS_URL="redis://..."
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | LLM model | gpt-4-turbo-preview |
| `UPLOAD_DIR` | File upload directory | ./uploads |
| `FAISS_INDEX_PATH` | Vector store path | ./data/faiss |

## Scaling Considerations

### 10k+ Users

1. **Auto-scaling**: Configure ECS/Cloud Run auto-scaling based on request count
2. **Read Replicas**: Add PostgreSQL read replicas for read-heavy workloads
3. **Vector DB Migration**: Move from FAISS to Pinecone/Weaviate for better scaling
4. **CDN**: Add CloudFront/Cloud CDN for static assets
5. **Rate Limiting**: Implement API gateway rate limiting

### Performance Tuning

```python
# Connection pooling
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10

# Embedding batching
EMBEDDING_BATCH_SIZE = 100

# Redis caching
CACHE_TTL = 3600  # 1 hour
```

## Monitoring

### Prometheus Metrics

- Request latency (histogram)
- Request count (counter)
- Error rate (counter)
- Document processing time (histogram)
- LLM token usage (counter)

### Logging

- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Integration: CloudWatch Logs / Stackdriver

### Alerts

- High error rate (>5%)
- High latency (p95 > 2s)
- Database connection exhaustion
- Redis memory usage > 80%

## Security

1. **HTTPS/TLS**: Always use HTTPS in production
2. **Secrets**: Use AWS Secrets Manager / GCP Secret Manager
3. **VPC**: Run services in private subnets
4. **WAF**: Add WAF rules for API protection
5. **CORS**: Configure allowed origins

## Backup & Recovery

- Daily PostgreSQL automated backups (7-day retention)
- Redis AOF persistence
- FAISS index snapshots to S3
- Disaster recovery plan documentation
