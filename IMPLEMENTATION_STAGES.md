# Implementation Stages

## Stage 1 --- FastAPI foundation

Built the initial application boundary.

Key components:

``` text
app/main.py
app/config.py
app/schemas.py
```

Endpoints included:

``` text
GET  /health
POST /api/v1/chat
```

Learned:

-   FastAPI application structure
-   Pydantic request/response contracts
-   environment-driven configuration
-   conversation ID creation

------------------------------------------------------------------------

## Stage 2 --- LangGraph fundamentals

Added a stateful graph with deterministic routing.

Initial workflow:

``` text
START
  |
classify_intent
  |
  +--> retrieve
  +--> operational
  +--> general
  |
respond
  |
 END
```

Introduced:

-   `StateGraph`
-   `AgentState`
-   graph nodes
-   fixed edges
-   conditional edges
-   async `ainvoke()`

The first classifier was deterministic so orchestration could be
understood before adding LLM uncertainty.

------------------------------------------------------------------------

## Stage 3 --- Real LLM integration and structured routing

Replaced the mock classifier with an LLM classifier.

Added:

``` text
app/llm/factory.py
app/llm/schemas.py
```

The classifier used a Pydantic structured output contract containing:

``` text
intent
confidence
reasoning
```

A deterministic confidence policy remained in Python.

Key lesson:

``` text
LLM = probabilistic semantic decision
application = deterministic policy/control
```

An evaluation dataset was also introduced to measure routing accuracy.

------------------------------------------------------------------------

## Stage 4 --- Enterprise tool calling

Created a mock enterprise REST API and real HTTP-backed tools.

Tools:

``` text
get_deployment
get_incidents
get_service_logs
```

Architecture:

``` text
enterprise agent
  -> model chooses registered tool
  -> ToolNode executes
  -> OperationsClient calls API
  -> ToolMessage returned
  -> model synthesizes answer
```

Important lesson:

``` text
bind_tools()
```

registers tool schemas with the model but does not execute them.

The registered tool set also forms an application capability boundary.

------------------------------------------------------------------------

## Stage 5 --- PostgreSQL + pgvector RAG

Replaced mock knowledge retrieval with a real vector retrieval pipeline.

Infrastructure:

``` text
PostgreSQL
+
pgvector
```

Table:

``` text
knowledge_chunks
```

Knowledge ingestion:

``` text
Markdown
 -> chunk
 -> embed
 -> upsert into PostgreSQL
```

Retrieval:

``` text
query
 -> query embedding
 -> cosine-distance pgvector search
 -> similarity threshold
 -> relevant chunks
```

Important database behavior:

``` sql
ON CONFLICT (document_id, chunk_index)
DO UPDATE ...
```

was used to make repeated ingestion idempotent for an existing logical
chunk.

------------------------------------------------------------------------

## Stage 6 --- Unified enterprise agent

The architecture was simplified from separate operational and RAG
branches to one bounded enterprise capability.

Before:

``` text
classifier
  -> RAG OR tools
```

After:

``` text
classifier
  -> enterprise agent
       -> tools
       -> RAG
       -> multiple capabilities if required
```

RAG became an agent tool:

``` text
search_knowledge
```

This enables hybrid questions such as:

> Investigate PAY-2026-0812 and tell me what our rollback runbook
> recommends.

The agent can retrieve both operational facts and documentation in the
same workflow.

------------------------------------------------------------------------

## Stage 7 --- Redis

Redis was introduced for three concrete application concerns.

### Conversation state

Conversation history is serialized and stored using:

``` text
conversation:{conversation_id}
```

### Cache

Read-only operational responses can be cached with a TTL.

Example:

``` text
deployment:PAY-2026-0812
```

### Rate limiting

A fixed-window counter provides basic request throttling.

Example:

``` text
rate_limit:{client_id}
```

Request lifecycle became:

``` text
request
 -> rate limit
 -> load conversation
 -> LangGraph
 -> save conversation
 -> response
```

Key lesson:

LangGraph state is transient execution state. Redis provides shared
state across requests and application replicas.

------------------------------------------------------------------------

## Stage 8 --- Local open-weight model with Ollama

The POC added an actual locally served open-weight model.

**vLLM is not used.**

Current architecture:

``` text
enterprise agent
 -> OpenAI-compatible client
 -> Ollama
 -> open-weight model
 -> local Mac hardware
```

The classifier can remain on a hosted OpenAI model while the enterprise
agent uses the local model.

Provider-specific configuration is hidden behind the model factory.

Tests covered:

-   basic model invocation
-   structured output capability
-   tool calling
-   full LangGraph execution
-   RAG generation
-   hosted-vs-local comparison

Key lesson:

A model being able to generate good chat responses does not guarantee
reliable:

``` text
structured output
tool calling
argument extraction
multi-tool reasoning
```

Those capabilities must be evaluated separately.

### Future option

With GPU infrastructure, Ollama could later be replaced by another
OpenAI-compatible serving layer such as vLLM.

That is future work and is not part of this POC.

------------------------------------------------------------------------

## Stage 9 --- Production resilience

**Skipped for the POC.**

Topics intentionally not deeply implemented include:

-   circuit breakers
-   sophisticated retry policies
-   detailed failure taxonomy
-   model failover policies
-   fault injection
-   production-grade retry/idempotency design
-   complex graceful degradation

Reason:

The objective of the POC is to demonstrate the core GenAI application
architecture rather than production reliability engineering at full
depth.

------------------------------------------------------------------------

## Stage 10 --- Langfuse observability and evaluation

Added GenAI-specific observability and evaluation.

The goal was to answer questions such as:

``` text
Which model ran?
What route was selected?
Which tools were called?
What evidence was retrieved?
How long did the model call take?
Why did an evaluation case fail?
```

Evaluation cases exercise agent behavior instead of only checking
whether an HTTP request returned `200`.

Useful evaluation dimensions include:

-   expected tool selection
-   argument extraction
-   knowledge retrieval
-   grounded answer quality
-   hybrid tool + RAG behavior
-   latency
-   local vs hosted model behavior

This creates a feedback loop:

``` text
test dataset
 -> run application
 -> inspect result
 -> inspect Langfuse trace
 -> identify failure
 -> improve prompt/tool/retrieval/model
 -> rerun
```

------------------------------------------------------------------------

## Stage 11 --- Dockerized local stack

Containerized the application and supporting services.

Docker Compose runs:

``` text
genai-api
mock-enterprise-api
PostgreSQL + pgvector
Redis
```

Ollama remains on the Mac host.

Important networking configuration:

``` text
Postgres:
postgres:5432

Redis:
redis:6379

Mock API:
mock-enterprise-api:8001

Ollama on Mac:
host.docker.internal:11434
```

Learned:

-   Dockerfile construction
-   `.dockerignore`
-   images vs containers
-   persistent volumes
-   Compose service discovery
-   health checks
-   environment overrides
-   container-to-container networking
-   host-to-container networking

The evaluation suite can also be run inside the application container.

------------------------------------------------------------------------

## Stage 12 --- Kubernetes / OpenShift

**Not included in the current POC.**

The project stops at Stage 11.

Kubernetes/OpenShift remains a future deployment exercise when an
appropriate local or remote cluster environment is available.

The Dockerized application already establishes the deployment boundaries
needed for a later migration:

``` text
containerized stateless API
external Redis
external PostgreSQL
service-based enterprise API
model-serving endpoint
environment-driven configuration
```
