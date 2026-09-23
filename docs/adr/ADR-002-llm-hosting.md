# ADR-002: LLM Hosting Strategy

## Status

Accepted

## Context

The Regulatory Compliance Assistant requires an LLM to:

- Generate answers from retrieved regulatory evidence
- Explain compliance findings
- Handle natural-language regulatory questions
- Support the transaction compliance workflow

The assignment requires an open-source prototype and specifically
expects production awareness around model selection, fallback,
cost controls, security and regulatory sensitivity.

## Decision

Use an open-source model hosted locally for the prototype.

The prototype uses:

- Qwen3 1.7B
- GGUF quantized model
- llama.cpp / llama-server
- Local HTTP inference endpoint

The RAG system sends only the retrieved regulatory evidence
and user question to the model.

The model is instructed to:

- Use only retrieved evidence
- Avoid inventing regulations
- State when information is insufficient
- Provide source attribution

## Alternatives Considered

### Managed Foundation Model API

Examples include commercial cloud-hosted LLM services.

Advantages:

- Higher model capability
- Managed infrastructure
- Easier scaling
- Faster access to newer models

Disadvantages:

- External data processing considerations
- Potential regulatory/data-residency concerns
- API cost increases with usage
- Vendor dependency
- Requires controls to prevent regulated information
  from being sent outside approved environments

A managed model can be introduced in production only after
security, residency, contractual and compliance requirements
are satisfied.

### Larger Self-Hosted Open-Source Model

Advantages:

- Greater control over data
- No per-token external API dependency
- Can be deployed inside a controlled environment

Disadvantages:

- Higher GPU requirements
- Higher infrastructure cost
- More operational complexity
- Model serving and scaling become platform responsibilities

## Consequences

### Positive

- Prototype does not depend on a paid LLM API
- Sensitive regulatory evidence remains local
- Model behavior can be controlled
- Reproducible development environment

### Negative

- Small local model has lower reasoning capability than
  larger foundation models
- Local inference has limited throughput
- Production deployment requires GPU infrastructure
- Model quality must be evaluated before production use

## Production Strategy

Use a model gateway abstraction rather than directly coupling
the application to one model provider.

Example:

Application
    |
    v
Model Gateway
    |
    +---- Primary approved model
    |
    +---- Fallback model
    |
    +---- Local/self-hosted model

The gateway should track:

- Latency
- Token usage
- Cost
- Model version
- Error rate
- Quality evaluation results

Models should be versioned and evaluated before replacement.

## Security Controls

The production system should include:

- Data classification
- PII / sensitive-data detection
- Prompt and output filtering
- Encryption
- Access control
- Audit logging
- Approved model allow-list
- Data residency controls