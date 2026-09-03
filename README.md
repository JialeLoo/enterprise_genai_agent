# Enterprise GenAI Operations Copilot

A hands-on proof of concept for an enterprise GenAI application that
combines:

-   FastAPI as the application/API layer
-   LangGraph for stateful workflow orchestration
-   Hosted OpenAI models for classification
-   A local open-weight model served through Ollama
-   An OpenAI-compatible model gateway
-   Enterprise tool calling
-   Retrieval-Augmented Generation (RAG)
-   PostgreSQL + pgvector for vector retrieval
-   Redis for conversation state, caching, and rate limiting
-   Langfuse for tracing and evaluation
-   Docker / Docker Compose for the local application stack

## POC scope

Implemented through **Stage 11**.

  Stage   Topic                                            Status
  ------- ------------------------------------------------ ------------------------------
  1       FastAPI foundation                               Completed
  2       LangGraph fundamentals                           Completed
  3       Hosted LLM + structured routing                  Completed
  4       Enterprise tool calling                          Completed
  5       PostgreSQL + pgvector RAG                        Completed
  6       Unified enterprise agent: tools + RAG            Completed
  7       Redis conversation state, cache, rate limiting   Completed
  8       Local open-weight model serving with Ollama      Completed
  9       Production resilience                            **Skipped for POC**
  10      Langfuse observability + evaluation              Completed
  11      Dockerized local stack                           Completed
  12      Kubernetes / OpenShift                           **Out of current POC scope**
  13+     Security / further production hardening          Future work

> Stage 8 uses **Ollama**, not vLLM. vLLM is only a possible future
> production serving replacement when GPU infrastructure is available.

## Final architecture

``` text
                         Client
                           |
                           v
                        FastAPI
                           |
                           v
                        LangGraph
                           |
                +----------+----------+
                |                     |
           classifier           enterprise agent
                |                     |
          model gateway          model gateway
                |                     |
             OpenAI        OpenAI-compatible API
                                      |
                                    Ollama
                                      |
                              open-weight model
                                      |
                               local hardware
                                      |
                         +------------+------------+
                         |                         |
                       tools                      RAG
                         |                         |
                 enterprise API            PostgreSQL
                                              +
                                           pgvector

Redis
  - conversation state
  - cache
  - rate limiting

Langfuse
  - traces
  - model/tool visibility
  - evaluation
```

## Main use case

Example request:

> Investigate deployment PAY-2026-0812 and tell me what our rollback
> runbook recommends.

The application can combine live operational evidence and static
enterprise knowledge:

``` text
request
  -> FastAPI
  -> LangGraph classifier
  -> enterprise agent
  -> get_deployment tool
  -> mock enterprise API
  -> search_knowledge tool
  -> embedding + pgvector retrieval
  -> enterprise agent synthesis
  -> grounded response
```

## Local deployment

Stage 11 runs these components with Docker Compose:

``` text
Docker Compose
├── genai-api
├── mock-enterprise-api
├── PostgreSQL + pgvector
└── Redis

Mac host
└── Ollama + open-weight model
```

The API container reaches host Ollama through:

``` text
http://host.docker.internal:11434/v1
```

See the other documentation files for architecture, implementation
stages, component responsibilities, testing, and future work.
