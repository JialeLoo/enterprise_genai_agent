# Architecture

## 1. System overview

The Enterprise GenAI Operations Copilot is designed as an enterprise
application rather than a single LLM prompt.

``` text
User
 |
 v
FastAPI
 |
 v
LangGraph
 |
 +--> classifier
 |      |
 |      +--> hosted OpenAI model
 |
 +--> enterprise agent
        |
        +--> local open-weight model through Ollama
        |
        +--> enterprise tools
        |      |
        |      +--> deployment API
        |      +--> incident API
        |      +--> service logs API
        |
        +--> RAG tool
               |
               +--> embeddings
               +--> PostgreSQL
               +--> pgvector
```

Redis sits outside individual graph executions and provides shared
runtime state.

Langfuse provides observability around model calls, tool use, latency,
and evaluation.

## 2. Application boundary

### FastAPI

FastAPI is the external application boundary.

Responsibilities:

-   expose HTTP endpoints
-   validate request/response schemas
-   create/reuse conversation IDs
-   enforce rate limits
-   load conversation history
-   invoke LangGraph
-   persist updated conversation state
-   return the final answer

FastAPI does not contain the core agent decision logic.

### LangGraph

LangGraph is the orchestration layer.

Responsibilities:

-   maintain execution state
-   execute nodes
-   route between application capabilities
-   run the enterprise agent/tool loop
-   preserve message state during graph execution

The key distinction is:

``` text
FastAPI = application/API lifecycle
LangGraph = AI workflow lifecycle
```

## 3. Routing

The classifier performs coarse-grained routing:

``` text
enterprise_query
general_question
```

The classifier does **not** decide exact enterprise tools.

For enterprise queries, the enterprise agent receives a bounded
registered tool set and performs fine-grained capability selection.

``` text
classifier
    |
    +--> general
    |
    +--> enterprise agent
              |
              +--> get_deployment
              +--> get_incidents
              +--> get_service_logs
              +--> search_knowledge
```

This prevents the architecture from becoming one unrestricted giant
agent.

## 4. Model gateway

The application uses model factory functions rather than directly
hard-coding a model into every node.

Example provider split:

``` text
classifier
  -> OpenAI hosted model

enterprise agent
  -> ChatOpenAI-compatible client
  -> Ollama /v1 endpoint
  -> local open-weight model
```

The local model is accessed through an OpenAI-compatible API.

This isolates model serving from orchestration.

### Current POC

``` text
LangGraph
  -> OpenAI-compatible client
  -> Ollama
  -> open-weight model
  -> local Mac hardware
```

### Possible future production design

``` text
LangGraph
  -> OpenAI-compatible client
  -> GPU inference service
  -> open-weight model
```

vLLM is a possible future inference server, but **it is not used in this
POC**.

## 5. Enterprise tools

The POC provides read-only enterprise tools:

``` text
get_deployment
get_incidents
get_service_logs
```

Each tool wraps an application client rather than embedding HTTP
implementation throughout agent code.

``` text
LLM tool call
   |
ToolNode
   |
Python @tool
   |
OperationsClient
   |
enterprise REST API
```

`bind_tools()` exposes schemas to the model. It does not execute the
tools.

LangGraph `ToolNode` performs the actual execution.

## 6. RAG

Enterprise documentation is stored as chunks.

``` text
Markdown documents
   |
chunking
   |
embedding
   |
knowledge_chunks
   |
PostgreSQL + pgvector
```

At query time:

``` text
query
 |
embedding
 |
vector similarity search
 |
top relevant chunks
 |
enterprise agent
 |
grounded answer
```

The RAG capability is exposed to the enterprise agent as:

``` text
search_knowledge
```

This is important because a single request may need both live
operational data and documentation.

## 7. Redis

Redis serves three different purposes.

### Conversation state

``` text
conversation:{conversation_id}
```

Conversation messages survive across HTTP requests and can be loaded
into a new LangGraph execution.

### Tool cache

Example:

``` text
deployment:PAY-2026-0812
```

Repeated read-only calls can avoid unnecessary downstream requests for a
short TTL.

### Rate limiting

Example:

``` text
rate_limit:{client_id}
```

The POC uses a simple fixed-window counter.

## 8. State model

There are two distinct types of state:

``` text
LangGraph AgentState
= transient state during one graph execution

Redis
= external state across HTTP requests
```

The request lifecycle is:

``` text
HTTP request
  -> Redis rate limit
  -> Redis conversation load
  -> deserialize messages
  -> LangGraph AgentState
  -> graph execution
  -> serialize messages
  -> Redis conversation save
  -> HTTP response
```

## 9. Observability

Langfuse is used to make GenAI behavior inspectable.

Important things to observe include:

-   request / conversation context
-   classifier decision
-   model/provider used
-   model latency
-   tool calls
-   tool arguments
-   retrieved evidence
-   failures
-   evaluation results

The goal is not simply application logging. GenAI observability needs
visibility into the reasoning workflow and evidence path.

## 10. Deployment topology after Stage 11

``` text
                       Mac host
                          |
                       Ollama
                          |
                  host.docker.internal
                          |
                          v
                    genai-api
                   Docker container
                          |
             +------------+-------------+
             |            |             |
             v            v             v
          postgres      redis      mock-enterprise-api
          container    container       container
```

Docker Compose provides service DNS:

``` text
postgres:5432
redis:6379
mock-enterprise-api:8001
```

`localhost` inside `genai-api` refers to the API container itself, not
the Mac and not other containers.
