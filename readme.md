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