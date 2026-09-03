# Design Decisions and Future Work

## Current POC boundary

The project intentionally stops at Stage 11.

Implemented:

``` text
FastAPI
LangGraph
hosted LLM classification
local open-weight model
Ollama
OpenAI-compatible model abstraction
enterprise tool calling
RAG
PostgreSQL
pgvector
Redis
Langfuse
evaluation
Docker Compose
```

Not implemented in the current POC:

``` text
vLLM
deep Stage 9 resilience
Kubernetes
OpenShift
production authentication/authorization
human approval for mutation tools
production secrets management
full CI/CD
production HA
```

------------------------------------------------------------------------

## Decision 1 --- Ollama instead of vLLM

The goal of Stage 8 was to obtain hands-on open-weight model experience
without requiring GPU infrastructure.

Therefore the POC uses:

``` text
Ollama
+
local open-weight model
+
OpenAI-compatible API
```

This provides practical exposure to:

-   local model serving
-   model selection
-   quantization/resource constraints
-   tool-calling compatibility
-   structured-output compatibility
-   latency differences
-   hosted-vs-local evaluation
-   provider abstraction

vLLM would add production-oriented GPU inference concerns such as:

``` text
GPU scheduling
continuous batching
higher throughput
concurrency
GPU memory management
model-serving capacity
```

It remains a future option rather than part of this POC.

------------------------------------------------------------------------

## Decision 2 --- Stage 9 skipped

The POC does not attempt to implement production resilience at full
depth.

Skipped areas include:

-   circuit breakers
-   advanced retry/backoff policies
-   comprehensive error taxonomy
-   model/provider failover
-   fault injection
-   production-grade graceful degradation

Basic timeouts/retries already present in libraries may remain, but
reliability engineering is not a primary POC objective.

A production implementation would revisit this before release.

------------------------------------------------------------------------

## Decision 3 --- Kubernetes/OpenShift not required for current POC

Stage 12 was explored conceptually but is not included in the
implementation scope.

The project remains locally deployable through Docker Compose.

This is sufficient to demonstrate:

``` text
containerization
service boundaries
networking
environment-based configuration
persistent database storage
shared Redis state
external model serving
```

When a Kubernetes environment is available, the Dockerized components
can become the basis for Deployments/Services/ConfigMaps/Secrets/PVCs.

------------------------------------------------------------------------

## Decision 4 --- Hosted classifier + local enterprise agent

The initial Stage 8 configuration intentionally isolates the local model
experiment.

``` text
classifier
 -> hosted OpenAI model

enterprise agent
 -> Ollama
 -> local open-weight model
```

This avoids changing every AI dependency simultaneously.

It also enables direct comparison between:

``` text
hosted model reliability
vs.
local model reliability
```

A future version could move classification and embeddings to local
models if data-residency or offline requirements demand it.

------------------------------------------------------------------------

## Decision 5 --- Hosted embeddings retained

The POC keeps the existing embedding provider while introducing local
generation.

Reason:

``` text
change one architectural dimension at a time
```

The RAG system can later use a local embedding model, but doing so is
not required to demonstrate the local open-weight generation path.

------------------------------------------------------------------------

## Decision 6 --- RAG exposed as a tool

Rather than maintaining separate:

``` text
operational branch
knowledge branch
```

the final enterprise workflow exposes:

``` text
search_knowledge
```

alongside operational tools.

This allows the model to gather multiple forms of evidence for one
request.

The classifier only determines whether enterprise capabilities are
required.

------------------------------------------------------------------------

## Decision 7 --- Redis is runtime state, not durable truth

Redis is used for:

``` text
conversation state
cache
rate limiting
```

PostgreSQL remains the durable knowledge data store.

A production system may also persist audit/conversation records
elsewhere depending on regulatory and business requirements.

------------------------------------------------------------------------

## Decision 8 --- Read-only tools only in the POC

The current tools retrieve information.

They do not:

``` text
rollback deployments
restart services
modify incidents
change access
write production data
```

This keeps the POC safe and avoids pretending that an LLM prompt is an
authorization mechanism.

A future mutation workflow should include:

``` text
authenticated identity
authorization
explicit tool permissions
validation
approval gates where appropriate
idempotency
audit records
```

------------------------------------------------------------------------

# Future roadmap

## A. Security and approval controls

Add:

``` text
OIDC/JWT authentication
user/tenant context
RBAC/ABAC
tool-level permissions
human approval for sensitive actions
audit logs
prompt-injection boundaries
```

## B. Production resilience

Add the skipped Stage 9 capabilities:

``` text
timeout budgets
retry classification
exponential backoff + jitter
circuit breakers
bounded tool loops
graceful degradation
fault injection tests
```

## C. Local embeddings

Possible future path:

``` text
hosted embeddings
 -> local embedding model
```

Then the system could reduce dependence on external AI APIs.

## D. Production open-weight serving

When GPU infrastructure exists:

``` text
Ollama
 -> production inference service
```

vLLM is one possible option.

The desired application boundary remains:

``` text
LangGraph
 -> OpenAI-compatible API
 -> inference server
```

## E. Kubernetes / OpenShift

Containerized components can later be mapped to:

``` text
genai-api -> Deployment + Service
Redis -> managed service or deployment
PostgreSQL -> managed/enterprise DB or operator
configuration -> ConfigMap
secrets -> Secret / enterprise secrets manager
model server -> GPU deployment/service
```

## F. CI/CD

Add:

``` text
lint
unit tests
agent evaluation
Docker build
image scan
registry push
environment deployment
post-deployment smoke tests
```

## G. Stronger evaluation

Expand beyond small deterministic cases to measure:

``` text
tool-call success rate
argument accuracy
retrieval recall
groundedness
hallucination rate
answer correctness
latency
token usage
local-vs-hosted quality
regression by prompt/model version
```

The evaluation suite should become a release gate for significant
prompt, model, tool, and retrieval changes.
