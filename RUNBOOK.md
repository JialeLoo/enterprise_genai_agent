# Local Development and POC Runbook

## 1. Runtime components

The Stage 11 POC uses:

``` text
Docker Compose:
- genai-api
- mock-enterprise-api
- postgres
- redis

Mac host:
- Ollama
- local open-weight model

External, when configured:
- OpenAI
- Langfuse
```

## 2. Start Ollama

Verify Ollama:

``` bash
ollama --version
ollama list
```

Example model used during the POC:

``` bash
ollama pull qwen3:4b
ollama run qwen3:4b
```

Verify the OpenAI-compatible endpoint:

``` bash
curl http://localhost:11434/v1/models
```

## 3. Start Docker stack

``` bash
docker compose up -d --build
```

Inspect:

``` bash
docker compose ps
```

Expected services:

``` text
genai-api
genai-mock-enterprise-api
genai-postgres
genai-redis
```

## 4. Inspect logs

All services:

``` bash
docker compose logs
```

GenAI API:

``` bash
docker compose logs -f genai-api
```

## 5. Health checks

GenAI API:

``` bash
curl http://localhost:8000/health
```

Mock enterprise API:

``` bash
curl http://localhost:8001/health
```

Redis:

``` bash
docker compose exec redis redis-cli ping
```

Expected:

``` text
PONG
```

## 6. Verify PostgreSQL

``` bash
docker compose exec postgres \
  psql -U genai -d genai \
  -c "SELECT 1;"
```

Check knowledge:

``` bash
docker compose exec postgres \
  psql -U genai -d genai \
  -c "SELECT COUNT(*) FROM knowledge_chunks;"
```

## 7. Ingest knowledge

If the knowledge table is empty:

``` bash
docker compose exec genai-api \
  python -m scripts.ingest_knowledge
```

Then verify:

``` bash
docker compose exec postgres \
  psql -U genai -d genai \
  -c "
    SELECT document_id, title, chunk_index
    FROM knowledge_chunks
    ORDER BY id;
  "
```

## 8. Verify Ollama from the API container

``` bash
docker compose exec genai-api \
  python -c "
import httpx
r = httpx.get(
    'http://host.docker.internal:11434/v1/models'
)
print(r.status_code)
print(r.text[:1000])
"
```

Expected HTTP status:

``` text
200
```

## 9. Test operational query

``` bash
curl -X POST \
  http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Why did deployment PAY-2026-0812 fail?"
  }'
```

## 10. Test RAG query

``` bash
curl -X POST \
  http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What approvals are required before accessing production?"
  }'
```

## 11. Test hybrid query

``` bash
curl -X POST \
  http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Investigate PAY-2026-0812 and tell me what our rollback runbook recommends."
  }'
```

## 12. Inspect Redis

``` bash
docker compose exec redis redis-cli
```

Useful commands:

``` text
KEYS conversation:*
KEYS deployment:*
KEYS rate_limit:*
```

For local debugging only, inspect a conversation:

``` text
GET conversation:<conversation-id>
```

## 13. Run evaluation

``` bash
docker compose exec genai-api \
  python -m evaluation.evaluate_agent
```

Use Langfuse traces to investigate unexpected agent behavior.

## 14. Stop services

Preserve database and Redis volumes:

``` bash
docker compose down
```

Delete containers **and volumes**:

``` bash
docker compose down -v
```

`-v` deletes local PostgreSQL and Redis data. Re-ingestion will be
required.

## 15. Common networking reminder

When FastAPI runs directly on the Mac:

``` text
Postgres = localhost:5432
Redis = localhost:6379
Mock API = localhost:8001
Ollama = localhost:11434
```

When FastAPI runs inside Docker:

``` text
Postgres = postgres:5432
Redis = redis:6379
Mock API = mock-enterprise-api:8001
Ollama = host.docker.internal:11434
```

Inside a container, `localhost` means that container itself.
