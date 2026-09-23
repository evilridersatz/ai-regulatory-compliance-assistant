# ADR-001: Vector Database Selection

## Status

Accepted

## Context

The Regulatory Compliance Assistant needs to store embeddings
of regulatory document chunks and retrieve relevant evidence
for natural-language compliance questions.

The system must support:

- Semantic similarity search
- Metadata such as document, version, page and chunk ID
- Source attribution and auditability
- Local development for the prototype
- Future production scaling

Regulatory data is sensitive, so the architecture should also
support controlled deployment and data residency requirements.

## Decision

Use Qdrant as the vector database for the prototype.

The prototype uses the local persistent Qdrant deployment:

QdrantClient(path="data/qdrant")

The vector collection stores:

- Embedding vector
- Source document
- Page number
- Chunk ID
- Regulatory text

Cosine similarity is used for semantic retrieval.

## Alternatives Considered

### PostgreSQL + pgvector

Advantages:

- Existing relational database ecosystem
- SQL and vector search in one platform
- Useful when metadata and transactional data need to
  be queried together

Disadvantages:

- Requires PostgreSQL infrastructure
- Vector workloads may need additional scaling considerations

### Elasticsearch / OpenSearch

Advantages:

- Strong keyword search
- Supports hybrid search
- Mature search and filtering capabilities

Disadvantages:

- More infrastructure for a small prototype
- Higher operational complexity than required for the MVP

## Consequences

### Positive

- Simple local development
- Open-source technology
- Persistent local storage
- Metadata can be stored with vectors
- Easy integration with Python

### Negative

- The prototype deployment is not production-ready
- Production deployment requires backup, monitoring,
  authentication and scaling considerations
- Hybrid search may require additional search infrastructure
  depending on production scale

## Production Considerations

For production, the vector layer should be deployed with:

- Authentication and network controls
- Encryption in transit and at rest
- Backup and disaster recovery
- Monitoring
- Access controls
- Data residency controls

The vector database should not be treated as the only source
of regulatory truth. Original regulatory documents and their
versions must remain preserved for auditability.