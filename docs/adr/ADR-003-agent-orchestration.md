# ADR-003: Agent Orchestration

## Status

Accepted

## Context

The Compliance Assistant must perform multiple steps:

1. Understand the user's question or transaction
2. Retrieve regulatory evidence
3. Evaluate the transaction
4. Generate a compliance explanation
5. Provide citations
6. Handle insufficient information
7. Preserve state and execution information for auditability

The workflow may also need to call different tools such as:

- Regulatory knowledge retrieval
- Transaction risk rules
- Regulatory change analysis
- Report generation

The system therefore needs explicit workflow orchestration rather
than allowing an LLM to freely choose every action.

## Decision

Use LangGraph for the agentic workflow.

The prototype separates deterministic tools from LLM reasoning.

The planned workflow is:

START
  |
  v
Input Validation
  |
  v
Intent / Transaction Analysis
  |
  v
Regulatory Retrieval
  |
  v
Risk Rule Evaluation
  |
  v
LLM Compliance Assessment
  |
  v
Evidence Validation
  |
  v
Human Review if Required
  |
  v
Final Response
  |
 END

Each node has a defined responsibility.

## State

The workflow state should contain information such as:

- User query
- Transaction information
- Retrieved documents
- Retrieved chunks
- Risk factors
- Risk level
- Compliance assessment
- Required actions
- Citations
- Validation status
- Error information
- Workflow execution ID

## Alternatives Considered

### CrewAI

Advantages:

- Simple multi-agent abstraction
- Useful for role-based agent workflows
- Easy to prototype

Disadvantages:

- Multi-agent abstraction can add unnecessary complexity
- Regulatory workflows benefit from explicit deterministic
  state transitions

### Custom Python Workflow

Advantages:

- Maximum control
- Minimal dependencies
- Easy to understand

Disadvantages:

- State management must be implemented manually
- Retry handling becomes custom code
- Workflow observability becomes more difficult

### Direct LLM Agent Loop

Advantages:

- Very simple initial implementation
- Flexible tool selection

Disadvantages:

- Less predictable execution
- Harder to audit
- Greater risk of unnecessary tool calls
- More difficult to guarantee deterministic compliance rules

## Consequences

### Positive

- Explicit workflow state
- Better auditability
- Deterministic compliance rules can be separated from LLM
  reasoning
- Individual steps can be tested independently
- Failed steps can be retried
- Human review can be inserted for high-risk cases

### Negative

- Additional orchestration complexity
- More components to test
- State schema must be maintained as the workflow evolves

## Error Handling

The workflow should handle:

- Retrieval failure
- Empty retrieval results
- LLM timeout
- Invalid transaction input
- Unsupported regulatory question
- Insufficient regulatory evidence
- Model output validation failure

High-risk or uncertain cases should be routed to human review
rather than automatically producing a final compliance decision.

## Auditability

Each execution should generate an audit record containing:

- Execution ID
- Timestamp
- User/request identifier
- Input
- Retrieved document versions
- Retrieved chunks
- Model name and version
- Prompt/template version
- Risk-rule results
- Final assessment
- Citations
- Human review status