# AI Regulatory Compliance Assistant — Architecture Document

## 1. Executive Summary

This prototype implements an AI-powered regulatory compliance assistant for financial institutions. It is designed to support:

- Regulatory question answering with source citations
- Transaction compliance screening and risk identification
- Evidence-backed compliance analysis
- Audit-oriented traceability
- Evaluation of retrieval and answer quality

The prototype uses an open-source/local AI stack to reduce dependency on proprietary AI services. The current implementation uses local Qwen inference through llama.cpp, Qdrant for vector storage, BM25 for keyword retrieval, Sentence Transformers for embeddings, and a cross-encoder for reranking.

The architecture is intentionally designed with a separation between the working prototype and the production target architecture.

---

## 2. Business Requirements

The solution addresses the following requirements:

1. Compliance officers need fast access to regulatory requirements.
2. Answers should be grounded in regulatory evidence.
3. Responses should identify source documents and pages.
4. Compliance teams need transaction-level risk screening.
5. Internal auditors need traceable evidence for decisions.
6. Regulatory documents change over time, so document versions must be tracked.
7. The system must support security, access control, auditability, scalability, and data residency considerations.

---

## 3. Functional Architecture

### High-Level Flow

```text
                    ┌─────────────────────┐
                    │ Compliance User/API │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Query / Agent Layer │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       Regulatory Q&A                 Transaction Screening
                │                             │
                ▼                             ▼
       Hybrid Retrieval              Deterministic Risk Engine
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Cross-Encoder       │
                    │ Reranker            │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ LLM / Model Gateway │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Guardrails +        │
                    │ Evidence Validation │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Answer + Citations  │
                    └─────────────────────┘
```

---

## 4. Regulatory Document Ingestion

The ingestion pipeline processes regulatory PDF documents.

```text
Regulatory PDF
     │
     ▼
PDF Extraction
     │
     ▼
Page Metadata
     │
     ▼
Chunking
     │
     ▼
Embedding Generation
     │
     ▼
Qdrant Vector Store
```

Each chunk retains:

- Source document
- Page number
- Chunk ID
- Text
- Embedding

This metadata allows the final response to identify the regulatory evidence used.

### Current prototype

The prototype currently contains regulatory material covering RBI KYC and Basel guidance, together with a clearly identified synthetic RBI training document used for prototype testing.

The synthetic document is not treated as an official regulatory source.

---

## 5. Document Versioning

Regulatory documents can be amended or replaced. A production ingestion pipeline should maintain:

- Regulation ID
- Document title
- Issuing authority
- Effective date
- Publication date
- Version number
- Superseded version
- Ingestion timestamp
- Document hash

A new document version should be indexed without immediately deleting the previous version.

This allows historical compliance decisions to be reproduced using the regulatory version that was effective at the time.

---

## 6. Chunking Strategy

The current prototype extracts PDF pages and splits text into paragraph-based chunks.

The production implementation should improve this by making chunks aware of:

- Regulatory headings
- Sections
- Principles
- Paragraph numbers
- Tables
- Definitions
- Cross-references

A useful production metadata structure is:

```text
regulation_id
version
section
subsection
paragraph
page
effective_from
effective_to
text
```

This improves retrieval precision and auditability.

---

## 7. Embedding Layer

The prototype uses:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

The embedding dimension is 384.

The embedding model is local and open-source, allowing the prototype to operate without sending regulatory content to a third-party hosted embedding API.

For production, the embedding model should be versioned and evaluated whenever it is replaced.

---

## 8. Vector Database

The prototype uses Qdrant.

### Why Qdrant?

- Open-source
- Local deployment supported
- Vector similarity search
- Metadata payloads
- Suitable for containerized deployment
- Can be self-hosted for data residency requirements

The architecture keeps the vector database behind the application layer rather than exposing it directly to users.

---

## 9. Hybrid Retrieval

Pure vector search may miss exact regulatory terminology.

Pure keyword search may miss semantically equivalent questions.

Therefore the prototype combines:

```text
User Query
    │
    ├──────────────► BM25 Keyword Search
    │
    └──────────────► Semantic Vector Search
                         │
                         ▼
                 Candidate Combination
                         │
                         ▼
                    Top Candidates
```

The current implementation uses BM25 and Qdrant semantic retrieval and combines candidate results before reranking.

---

## 10. Cross-Encoder Reranking

The top candidates are passed to:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker scores the relationship between the question and each retrieved chunk.

```text
Hybrid Candidates
       │
       ▼
Cross Encoder
       │
       ▼
Re-ranked Evidence
       │
       ▼
Top-K Context
```

This reduces the likelihood that a semantically related but less relevant chunk is passed to the LLM.

---

## 11. LLM Architecture

The prototype uses:

```text
Qwen3-1.7B-Q4_K_M.gguf
          │
          ▼
       llama.cpp
          │
          ▼
localhost:8080/v1/chat/completions
```

The model is instructed to:

- Use only supplied regulatory evidence
- Avoid inventing regulations
- State when evidence is insufficient
- Produce evidence-grounded answers

### Production model gateway

For production, an AI/model gateway should sit between the application and model infrastructure.

Responsibilities:

- Authentication
- Authorization
- Model routing
- Model version management
- Rate limiting
- Retry/fallback
- Timeout handling
- Prompt versioning
- Token/cost tracking
- Observability

---

## 12. RAG Answer Generation

The final context contains source and page metadata.

Example:

```text
SOURCE: rbi_kyc_2025.pdf
PAGE: 46
CHUNK: 77

<regulatory evidence>
```

The LLM is instructed to answer only from this evidence.

The final response is accompanied by the source document and page information.

This provides a basic citation trail from:

```text
Question
   ↓
Retrieved Evidence
   ↓
LLM Answer
   ↓
Source/Page Citation
```

---

## 13. Transaction Compliance Workflow

The prototype includes a deterministic risk engine.

Example transaction:

```text
$2 million cross-border payment
+
high-risk jurisdiction
+
incomplete KYC
```

The deterministic engine identifies explicit risk factors before the LLM assessment.

```text
Transaction
     │
     ▼
Risk Rules
     │
     ├── High-risk jurisdiction
     ├── KYC incomplete
     └── Large cross-border transaction
     │
     ▼
Risk Level
     │
     ▼
Regulatory Retrieval
     │
     ▼
LLM Compliance Assessment
```

The LLM produces structured sections:

- Applicable regulations
- Potential compliance concerns
- Required actions
- Missing information

The deterministic rules and LLM reasoning are intentionally separated.

---

## 14. Guardrails

The prototype applies a grounding instruction:

> Answer only using the regulatory evidence provided.

When evidence is insufficient, the system can return:

```text
Insufficient information in the regulatory knowledge base.
```

Production guardrails should additionally include:

- Prompt injection detection
- PII controls
- Output schema validation
- Citation validation
- Unsupported-claim detection
- Maximum context limits
- Model timeout handling
- Human review for high-risk decisions

---

## 15. Agent / Orchestration Architecture

The compliance workflow separates deterministic processing from LLM generation.

Conceptually:

```text
Input Transaction
       │
       ▼
Risk Assessment
       │
       ▼
Regulatory Retrieval
       │
       ▼
Evidence Construction
       │
       ▼
LLM Assessment
       │
       ▼
Structured Compliance Result
```

For production, LangGraph can represent this workflow explicitly as a state graph.

Recommended state:

```text
transaction
risk_result
query
retrieved_documents
reranked_documents
llm_assessment
citations
errors
review_required
```

This allows retries, human review, and deterministic transitions.

---

## 16. Security

Production deployment should implement:

### Authentication

- Enterprise SSO
- OAuth/OIDC
- MFA where applicable

### Authorization

Role-based access control:

- Compliance Officer
- Compliance Head
- Internal Auditor
- Administrator

### Data Protection

- TLS in transit
- Encryption at rest
- Secret management
- Network isolation
- Private model endpoints
- Restricted vector database access

### Audit Logging

Record:

- User
- Timestamp
- Query
- Retrieved document IDs
- Regulatory versions
- Model version
- Prompt version
- Risk result
- Final response
- Human override/review

Sensitive raw content should be minimized in application logs.

---

## 17. Data Residency

Financial and regulatory information may be subject to organizational and jurisdictional requirements.

The production architecture should support region-specific deployment.

For example:

```text
India Data
   │
   ▼
India Region Infrastructure

EU Data
   │
   ▼
EU Region Infrastructure
```

Model and vector database processing should remain within the approved data boundary where required.

---

## 18. Scalability

The assignment target includes approximately:

- 500 concurrent users
- 10,000 queries/day

A production architecture can use:

```text
Load Balancer
      │
      ▼
API Gateway
      │
      ▼
Kubernetes / EKS
      │
      ├── API Pods
      ├── Retrieval Pods
      └── Agent Workers
              │
              ▼
        Model Gateway
              │
              ├── GPU Inference
              └── Fallback Model
```

### Scaling strategy

API and retrieval services should scale horizontally.

LLM inference should scale based on:

- Concurrent requests
- GPU utilization
- Queue depth
- Request latency

Long-running ingestion and evaluation jobs should be asynchronous.

---

## 19. Failure Handling

### Vector database unavailable

Return a controlled service error rather than generating an unsupported answer.

### LLM timeout

Retry within a bounded limit and use a configured fallback model where available.

### Embedding model unavailable

Do not silently generate embeddings with an incompatible model.

### Regulatory document ingestion failure

Keep the previous valid version active until the new version passes validation.

### Low retrieval confidence

Return an insufficient-evidence response or route to human review.

### Model deprecation

Maintain model/version metadata and test the replacement model against the evaluation dataset before promotion.

---

## 20. Observability

Production monitoring should track:

### Application Metrics

- Request count
- Error rate
- P50/P95/P99 latency
- Concurrent requests

### Retrieval Metrics

- Retrieval latency
- Top-K relevance
- Reranker latency
- No-result rate

### LLM Metrics

- Time to first token
- Generation latency
- Token usage
- Timeout rate
- Model errors

### Compliance Metrics

- High-risk transaction count
- Human review rate
- Unsupported-answer rate
- Citation coverage

---

## 21. Evaluation

The prototype contains a 20-question evaluation dataset with ground-truth answers.

The evaluation covers:

- RBI KYC
- Basel Core Principles
- Customer Due Diligence
- Transaction Monitoring
- High-Risk Relationships
- Compliance and Auditability

The current evaluation uses a lightweight custom keyword-overlap proxy.

This should not be interpreted as a formal RAGAS score.

A production evaluation framework should measure:

- Faithfulness
- Answer relevance
- Context precision
- Context recall
- Citation correctness
- Retrieval recall
- Latency
- Cost

Evaluation results are stored in:

```text
data/evaluation_results.json
```

Failure analysis is documented in:

```text
docs/evaluation_report.md
```

---

## 22. Cost and Latency Trade-offs

The prototype uses local inference to minimize dependency on paid model APIs.

Advantages:

- Data remains local
- No per-token hosted API charge
- Full control over model version

Trade-offs:

- Local GPU/CPU infrastructure is required
- Throughput may be lower
- Operational responsibility increases

A production model gateway allows routing based on query complexity.

Example:

```text
Simple FAQ
   → Smaller model

Complex regulatory analysis
   → Larger model

High-risk decision
   → Larger model + human review
```

Caching can reduce repeated retrieval and generation costs where appropriate.

---

## 23. Technology Stack

| Layer | Prototype |
|---|---|
| Language | Python |
| PDF processing | PyPDF |
| Embeddings | Sentence Transformers |
| Vector DB | Qdrant |
| Keyword retrieval | BM25 |
| Reranking | Cross Encoder |
| LLM | Qwen3 |
| Inference | llama.cpp |
| API | FastAPI |
| Orchestration | Workflow/agent components; LangGraph planned for explicit production state orchestration |
| Evaluation | Custom evaluation pipeline |

---

## 24. Architecture Decisions

Detailed architectural decisions are documented separately:

- `ADR-001-vector-database.md`
- `ADR-002-llm-hosting.md`
- `ADR-003-agent-orchestration.md`

These ADRs document the selected technologies, alternatives, and production trade-offs.

---

## 25. Prototype Limitations

The current implementation is a prototype.

Known limitations include:

1. The document set is smaller than a production regulatory corpus.
2. A synthetic RBI training document is included for prototype testing and is not an official regulatory source.
3. Regulatory version management is currently primarily documented as a production design rather than a complete automated update pipeline.
4. The current evaluation uses a lightweight custom metric rather than a full RAGAS implementation.
5. The local Qwen model has lower capacity than larger production models.
6. The prototype does not represent a production-grade compliance decision engine.
7. High-impact compliance decisions should remain subject to qualified human review.

---

## 26. Future Improvements

1. Add additional official RBI, BIS and MiFID II regulatory documents.
2. Implement automated regulatory document ingestion and version tracking.
3. Add section/principle-aware chunking.
4. Add metadata filtering.
5. Improve query expansion.
6. Normalize hybrid retrieval scores.
7. Add formal RAGAS evaluation.
8. Implement explicit LangGraph state orchestration.
9. Add human-in-the-loop approval for high-risk decisions.
10. Add production model gateway and model fallback.
11. Add distributed tracing and centralized observability.
12. Add automated regression evaluation for every document/model update.

---

## 27. Summary

The prototype demonstrates an end-to-end regulatory compliance AI architecture:

```text
Regulatory Documents
        ↓
PDF Extraction
        ↓
Chunking + Metadata
        ↓
Embeddings
        ↓
Qdrant
        +
BM25
        ↓
Hybrid Retrieval
        ↓
Cross-Encoder Reranking
        ↓
Local Qwen LLM
        ↓
Grounded Compliance Answer
        ↓
Citations + Audit Evidence
```

For transaction screening:

```text
Transaction
     ↓
Deterministic Risk Engine
     ↓
Regulatory Retrieval
     ↓
Reranking
     ↓
LLM Assessment
     ↓
Risk + Concerns + Actions
     ↓
Evidence / Human Review
```

The architecture separates the working prototype from production concerns and provides a path toward a secure, scalable and auditable enterprise regulatory compliance platform.





# AI Regulatory Compliance Assistant

An AI-powered regulatory compliance assistant prototype for financial institutions.

## Objective

The system provides:

- Regulatory question answering
- Cited regulatory evidence
- Transaction compliance screening
- Risk identification
- Compliance recommendations
- Audit-oriented evidence tracking

The prototype is designed around RBI KYC and Basel regulatory guidance.

## Architecture

```text
User / API
    |
    v
Query / Compliance Workflow
    |
    v
Hybrid Retrieval
(BM25 + Semantic Vector Search)
    |
    v
Cross-Encoder Reranker
    |
    v
Local Qwen LLM
    |
    v
Grounded Response + Regulatory Citations



Transaction
    |
    v
Deterministic Risk Rules
    |
    v
Regulatory Retrieval
    |
    v
LLM Compliance Assessment
    |
    v
Risk + Concerns + Required Actions


Technology Stack
Python 3.11
Qdrant
Sentence Transformers
BM25
Cross-Encoder reranking
Qwen3
llama.cpp
FastAPI
LangGraph
PyPDF
RAG Pipeline
Regulatory PDFs are loaded.
PDF pages are extracted.
Documents are split into chunks.
Chunks are converted into embeddings.
Embeddings are stored in Qdrant.
BM25 performs keyword retrieval.
Semantic search performs vector retrieval.
Candidate results are combined.
Cross-encoder reranking selects the most relevant evidence.
The local Qwen model generates a grounded answer.
Source document and page information are returned as citations.
Transaction Compliance

The prototype includes a deterministic risk engine that identifies
risk factors such as:

High-risk jurisdictions
Incomplete KYC
Large cross-border transactions

The regulatory evidence is then supplied to the LLM for a structured
compliance assessment.

Running the Project

Activate the virtual environment:

source .venv/bin/activate

Start the local Qwen model using llama.cpp:

~/Desktop/llama.cpp/build/bin/llama-server \
  -m ~/Desktop/models/Qwen3-1.7B-Q4_K_M.gguf \
  --port 8080 \
  --reasoning-budget 0

Build the vector database:

python -m app.rag.vector_store

Run a RAG question:

python -m app.rag.rag_answer

Run the compliance checker:

python -m app.agents.compliance_checker

Run evaluation:

export HF_HUB_OFFLINE=1
python -m app.evaluate
Evaluation

The evaluation dataset contains:

20 questions
20 ground-truth answers
RBI KYC
Basel Core Principles
Customer Due Diligence
Transaction Monitoring
High-Risk Relationships
Compliance and Auditability

Results are stored in:

data/evaluation_results.json

The detailed evaluation and failure analysis are documented in:

docs/evaluation_report.md
Documents

The prototype currently includes:

RBI KYC Directions 2025
Basel Core Principles
Basel Risk-Based Capital
Synthetic RBI KYC training document for prototype testing

The synthetic document is clearly identified as non-official and should
not be used as production regulatory evidence.

Production Considerations

For production deployment, the prototype would be extended with:

Managed Kubernetes
Model gateway and model fallback
Autoscaling inference
Document version management
Regulatory update pipelines
Metadata-based filtering
RBAC
Encryption
Audit logging
Observability
Retrieval and generation evaluation
Data residency controls
Backup and disaster recovery
Architecture Decisions

Three ADRs document major architectural decisions:

docs/adr/ADR-001-vector-database.md
docs/adr/ADR-002-llm-hosting.md
docs/adr/ADR-003-agent-orchestration.md
Limitations

This is a prototype and not a production regulatory decision system.

The evaluation currently uses a lightweight custom evaluation proxy.
Formal RAGAS evaluation can be added as a production evaluation
component.

Regulatory outputs should be reviewed by qualified compliance
professionals before being used for actual regulatory decisions.

Project Structure
app/
├── agents/
│   ├── compliance_checker.py
│   └── risk_engine.py
├── rag/
│   ├── chunk.py
│   ├── embed.py
│   ├── hybrid_search.py
│   ├── rag_answer.py
│   └── vector_store.py
├── evaluate.py
└── llm.py

data/
├── evaluation.json
├── evaluation_results.json
├── qdrant/
└── regulations/

docs/
├── architecture.md
├── evaluation_report.md
└── adr/
    ├── ADR-001-vector-database.md
    ├── ADR-002-llm-hosting.md
    └── ADR-003-agent-orchestration.md
