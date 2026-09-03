# Use Cases and Execution Flows

## 1. General question

Example:

> Hello, what can you do?

Flow:

``` text
FastAPI
 -> load conversation
 -> LangGraph
 -> classifier
 -> general_question
 -> general response
 -> save conversation
```

No enterprise tool or RAG lookup should be required.

------------------------------------------------------------------------

## 2. Operational investigation

Example:

> Why did deployment PAY-2026-0812 fail?

Flow:

``` text
FastAPI
 -> Redis rate limit
 -> Redis conversation load
 -> LangGraph
 -> classifier
 -> enterprise_query
 -> enterprise agent
 -> local model through Ollama
 -> get_deployment("PAY-2026-0812")
 -> ToolNode
 -> OperationsClient
 -> mock enterprise API
 -> deployment evidence
 -> enterprise agent
 -> final answer
 -> Redis conversation save
```

Example operational evidence:

``` text
deployment: PAY-2026-0812
service: payment-service
status: failed
reason: database connection timeout
```

The LLM does not invent the deployment status. It obtains it through the
registered tool.

------------------------------------------------------------------------

## 3. Incident investigation

Example:

> What incidents affect payment-service?

Potential flow:

``` text
enterprise agent
 -> get_incidents(service="payment-service")
 -> enterprise API
 -> incident records
 -> synthesis
```

The POC includes an incident associated with the payment-service
deployment.

------------------------------------------------------------------------

## 4. Log investigation

Example:

> Show me what happened in the payment-service logs.

Potential evidence includes:

``` text
connection pool exhausted
database timeout
circuit breaker threshold exceeded
```

Flow:

``` text
enterprise agent
 -> get_service_logs("payment-service")
 -> enterprise API
 -> logs
 -> model synthesis
```

------------------------------------------------------------------------

## 5. Internal policy question

Example:

> What approvals are required before accessing production?

Flow:

``` text
classifier
 -> enterprise agent
 -> search_knowledge
 -> embed query
 -> PostgreSQL / pgvector
 -> production access policy chunks
 -> agent
 -> grounded answer
```

Relevant documentation states concepts such as:

``` text
engineering manager approval
production owner approval
individual accounts
least privilege
break-glass controls
```

------------------------------------------------------------------------

## 6. Hybrid operational + RAG question

This is the main showcase use case.

Example:

> Deployment PAY-2026-0812 failed. Investigate what happened and tell me
> what our rollback runbook says we should do next.

Potential flow:

``` text
User
 |
FastAPI
 |
LangGraph
 |
classifier
 |
enterprise agent
 |
 +--> get_deployment
 |      |
 |      +--> enterprise API
 |
 +--> get_service_logs
 |      |
 |      +--> enterprise API
 |
 +--> search_knowledge
        |
        +--> embeddings
        +--> pgvector
        +--> rollback runbook
 |
enterprise agent synthesis
 |
answer
```

The final response should distinguish:

``` text
Observed operational facts
vs.
Documented internal guidance
```

This is why combining RAG and enterprise tools inside the bounded
enterprise agent is more useful than forcing the classifier to choose
only one branch.

------------------------------------------------------------------------

## 7. Multi-turn conversation

Turn 1:

> Investigate PAY-2026-0812.

The API returns a `conversation_id`.

Turn 2 using the same ID:

> What should we do next?

Flow:

``` text
request 2
 -> conversation_id
 -> Redis
 -> previous messages
 -> LangGraph AgentState
 -> model sees relevant conversation history
 -> response
 -> Redis updated
```

Redis therefore decouples conversation state from a particular Python
process.

------------------------------------------------------------------------

## 8. Cached tool call

First request:

``` text
get_deployment("PAY-2026-0812")
 -> cache miss
 -> enterprise API
 -> save Redis TTL cache
```

Repeated request:

``` text
get_deployment("PAY-2026-0812")
 -> Redis cache hit
 -> avoid downstream API call
```

This is appropriate for read-only data when the TTL reflects how quickly
the underlying data can change.

------------------------------------------------------------------------

## 9. Rate-limited request

Each request increments:

``` text
rate_limit:{client_id}
```

If the configured fixed-window limit is exceeded:

``` text
FastAPI
 -> HTTP 429
```

The POC uses client IP for simplicity. A production system should
normally rate-limit by authenticated user, API client, or tenant
identity.

------------------------------------------------------------------------

## 10. Dockerized execution

After Stage 11:

``` text
Client on Mac
 |
localhost:8000
 |
Docker port mapping
 |
genai-api container
 |
 +--> redis:6379
 +--> postgres:5432
 +--> mock-enterprise-api:8001
 +--> host.docker.internal:11434/v1
          |
        Ollama
          |
        local open-weight model
```

This validates the same application across explicit service boundaries
rather than relying on everything running as local Python processes.
