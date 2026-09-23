# Regulatory Compliance Assistant — Evaluation Report

## 1. Evaluation Objective

The evaluation measures the quality of the regulatory RAG pipeline using
20 question-answer pairs covering customer due diligence, KYC,
high-risk customers, transaction monitoring, record keeping,
Basel guidance and compliance functions.

## 2. Evaluation Dataset

- Total questions: 20
- Ground-truth answers: 20
- Regulatory domains:
  - RBI KYC
  - Basel Core Principles
  - Customer Due Diligence
  - Transaction Monitoring
  - High-Risk Relationships
  - Compliance and Auditability

## 3. Evaluation Method

Each question was processed through the complete RAG pipeline:

1. Query processing
2. BM25 keyword retrieval
3. Semantic vector retrieval
4. Hybrid candidate combination
5. Cross-encoder reranking
6. Local LLM generation
7. Ground-truth comparison

A lightweight keyword-overlap score was used as an initial evaluation
proxy. This is not a formal RAGAS metric.

## 4. Results

The initial 10-question evaluation produced an average
keyword-overlap score of 62.9%.

The evaluation was subsequently expanded to 20 questions.

The 20-question evaluation completed successfully and generated
`data/evaluation_results.json`.

## 5. Failure Analysis

### Basel Principle 29 retrieval

The system returned a generic answer about prudential regulations
instead of correctly identifying the specific customer due diligence
focus of Basel Principle 29.

This indicates a retrieval/reranking limitation for questions that
contain a specific regulatory principle reference.

### High-risk account query

The system returned:

"Insufficient information in the regulatory knowledge base."

However, other evaluation questions successfully retrieved evidence
covering enhanced due diligence and high-risk relationships.

This indicates that query wording can significantly affect retrieval.

### CDD retention query

The system returned insufficient information for the five-year
CDD record-retention question, while another evaluation query later
retrieved evidence containing the five-year retention requirement.

This indicates that the relevant evidence exists in the knowledge base
but was not consistently retrieved for every query formulation.

### Incomplete customer information

The system returned insufficient information for this query.

This represents another retrieval coverage gap rather than necessarily
a missing regulatory document.

### Regulatory evidence retention

The system also returned insufficient information for this question,
showing that retrieval performance varies depending on query phrasing.

## 6. Key Findings

The evaluation demonstrates that the prototype can successfully
retrieve and synthesize regulatory evidence for many common compliance
questions.

The main observed weakness is retrieval consistency for highly specific
regulatory concepts and alternative question formulations.

## 7. Planned Improvements

1. Improve query expansion for regulatory terminology.
2. Add metadata filtering by regulation, section and principle.
3. Improve chunking around regulatory headings and numbered principles.
4. Add stronger hybrid-search score normalization.
5. Improve reranking candidate selection.
6. Add document/version metadata.
7. Add dedicated retrieval tests for regulatory citations.
8. Evaluate with formal RAGAS metrics in the production evaluation
   pipeline.

## 8. Limitations

The current evaluation uses a lightweight custom keyword-overlap proxy
and should not be interpreted as a formal measurement of faithfulness,
answer relevance, context precision or context recall.

The prototype also uses a locally hosted Qwen model and a local Qdrant
database.

## 9. Conclusion

The prototype demonstrates an end-to-end regulatory compliance RAG
workflow with hybrid retrieval, reranking, grounded generation,
transaction screening and regulatory evidence tracking.

The evaluation identified specific retrieval failure modes that should
be addressed before production deployment.