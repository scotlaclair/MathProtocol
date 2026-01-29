# CLAUDE.md - AI Assistant Guide for MathProtocol

This document provides essential context and guidelines for AI assistants working on the MathProtocol codebase.

## Project Overview

**MathProtocol** is a deterministic LLM control protocol that forces Large Language Models to communicate using strict mathematical codes instead of free-form text. This prevents prompt injection attacks and enables LLMs to function as reliable logic engines in software pipelines.

**Version**: 2.1 (with Success Bit validation)
**License**: MIT
**Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12

## Quick Reference: Mathematical Sets

```
TASKS (Primes):      2, 3, 5, 7, 11, 13, 17, 19, 23, 29
PARAMETERS (Fib):    1, 2, 3, 5, 8, 13, 21, 34, 55, 89
RESPONSES (Pow2):    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096
TRAP PRIMES:         43, 47, 53, 59, 61  # DO NOT USE
```

## Protocol Format

**Input**: `[TASK]-[PARAM] | [CONTEXT]`
**Output**: `[RESPONSE]-[CONFIDENCE] | [PAYLOAD]`

### Task Code Mappings

| Code | Task | Type |
|------|------|------|
| 2 | Sentiment | Classification (no payload) |
| 3 | Summarization | Generative (requires payload) |
| 5 | LangDetect | Classification (no payload) |
| 7 | EntityExtract | Generative (requires payload) |
| 11 | Q&A | Generative (requires payload) |
| 13 | Classify | Classification (no payload) |
| 17 | Translate | Generative (requires payload) |
| 19 | Moderate | Classification (no payload) |
| 23 | Keywords | Generative (requires payload) |
| 29 | Readability | Classification (no payload) |

### Error Codes
- `1024`: Invalid Task
- `2048`: Invalid Parameter
- `4096`: Invalid Format

## Repository Structure

```
MathProtocol/
├── mathprotocol.py         # Core protocol engine (ProtocolRegistry, MathProtocol, MockLLM)
├── aegis_core.py           # Security layer (ContextFirewall, MerkleLogger, AegisGateway)
├── client_wrapper.py       # LLM API integration wrapper
├── exceptions.py           # Custom exception classes
├── mathprotocol_cli.py     # CLI for prompt composition
├── audit_viewer.py         # Audit log viewer
├── test_mathprotocol.py    # Protocol unit tests
├── test_aegis_core.py      # Security module tests
├── examples.py             # Usage examples
├── setup.py                # Package configuration
├── requirements.txt        # Dev dependencies (pytest, pytest-cov)
├── Dockerfile              # Container image
├── docs/
│   ├── ARCHITECTURE.md     # System design
│   ├── AEGIS_MODULE.md     # Security documentation
│   └── TECHNICAL_WHITE_PAPER.md
└── examples/high_assurance_aegis/
    ├── server.py           # FastAPI application
    ├── honeypot.py         # Active defense middleware
    └── docker-compose.yml  # Container orchestration
```

## Development Commands

```bash
# Run built-in tests
python mathprotocol.py

# Run test suite
pytest test_mathprotocol.py test_aegis_core.py -v

# Run with coverage
pytest --cov=mathprotocol --cov-report=term

# Run examples
python examples.py

# CLI usage
python mathprotocol_cli.py list        # Show all codes
python mathprotocol_cli.py compose     # Build protocol prompts
```

## Immutable Protocol Laws

These rules MUST NEVER be violated:

1. **Mathematical Determinism**: TASK=Prime, PARAM=Fibonacci, RESPONSE=Power of 2
2. **Task Type Safety**: Classification tasks (2, 5, 13, 19, 29) MUST NOT have payload; Generative tasks (3, 7, 11, 17, 23) MUST have payload
3. **Zero Natural Language in Control Flow**: Only CONTEXT field may contain natural language
4. **Security Logging**: All security events MUST be logged to Merkle Audit Chain
5. **PHI/PII Protection**: Sensitive data MUST be redacted before LLM processing

## Code Style Requirements

### Python Standards
- PEP 8 compliant
- 4-space indentation
- Max line length: ~100 characters
- Double quotes for strings

### Type Hints (Required)
```python
def validate_input(self, input_str: str) -> bool:
    ...

def parse_response(self, response_str: str) -> Dict[str, Any]:
    ...
```

### Docstrings (Google Style, Required)
```python
def validate_input(self, input_str: str) -> bool:
    """
    Validate if input matches protocol format.

    Args:
        input_str: The input string to validate

    Returns:
        True if valid format, False otherwise

    Raises:
        ValidationError: If input is None
    """
```

### Import Order
1. Standard library
2. Third-party packages
3. Local modules

## Security Guidelines

### Paranoid Mode (Default Behavior)
- Assume every variable input is malicious
- Never use `print()` - use `logger` or audit chain
- Fail secure: Raise `HTTPException(403)` or `500`, never return `None` silently

### Mandatory Patterns
```python
# String comparison - NEVER use ==
secrets.compare_digest(a, b)

# Random tokens - NEVER use random module
secrets.token_hex(16)

# Error handling - Preserve in Dead Letter Vault
try:
    ...
except Exception as e:
    vault.store(context, e)
    raise HTTPException(500, "Internal error")
```

### Forbidden Libraries
- `pickle` (insecure deserialization)
- `xml.etree` (XXE vulnerabilities - use `defusedxml`)
- `random` (non-cryptographic - use `secrets`)

### Regex Safety
Use atomic grouping to prevent ReDoS:
```python
# GOOD - atomic grouping
r'^(\d+)-(\d+)(?:\s{0,10}\|\s{0,10}(.+))?$'

# BAD - vulnerable to backtracking
r'^(\d+)-(\d+)(\s*\|\s*(.+))?$'
```

## Testing Requirements

### Before Submitting Changes
1. Run full test suite: `pytest test_mathprotocol.py test_aegis_core.py -v`
2. All tests must pass
3. Add tests for new functionality
4. Update tests for modified behavior

### Test Naming Convention
```python
def test_validate_input_with_valid_format():
    ...

def test_validate_response_classification_no_payload():
    ...
```

## Making Changes

### Before Modifying Code
1. Read the relevant documentation (ARCHITECTURE.md, AEGIS_MODULE.md)
2. Understand security implications
3. Review existing tests

### Change Guidelines
- **Minimal Changes**: Only modify what's necessary
- **Security First**: Never weaken security for convenience
- **No Secrets**: Never commit API keys, passwords, etc.
- **Test Thoroughly**: Add tests for new behavior
- **Document**: Update docstrings and docs if behavior changes

### Validation Logic Changes
When modifying `mathprotocol.py`:
1. Add corresponding tests in `test_mathprotocol.py`
2. Update `examples.py` if behavior changes
3. Update `SYSTEM_PROMPT.md` if LLM behavior changes

### Adding New Codes
1. Update appropriate constant set (PRIMES, FIBONACCI, POWERS_OF_2)
2. Add mapping in TASKS, PARAMS, or RESPONSES dict
3. Update README.md documentation
4. Add test coverage
5. Update SYSTEM_PROMPT.md

## Common Patterns

### Input Validation
```python
def validate_input(self, input_str: str) -> bool:
    if not input_str or not isinstance(input_str, str):
        return False

    pattern = r'^(\d+)-(\d+)(?:\s{0,10}\|\s{0,10}(.+))?$'
    match = re.match(pattern, input_str)
    if not match:
        return False

    task = int(match.group(1))
    param = int(match.group(2))

    return task in self.TASKS and param in self.FIBONACCI
```

### Response Validation (v2.1 with Success Bit)
```python
def validate_response(self, response_str: str, task_code: int) -> bool:
    parsed = self.parse_response(response_str)
    codes = parsed["codes"]
    payload = parsed["payload"]

    # v2.1: Success Bit validation (response must be odd)
    if codes and (codes[0] & 1) == 0:
        return False  # Missing Success Bit

    # Classification: no payload
    if task_code in self.CLASSIFICATION_TASKS:
        return payload == ""
    # Generative: requires payload
    elif task_code in self.GENERATIVE_TASKS:
        return payload != ""

    return True
```

## Anti-Patterns to Avoid

```python
# BAD: Natural language in protocol
task = "sentiment analysis"

# GOOD: Mathematical codes only
task = 2

# BAD: Payload in classification response
return "2-128 | The sentiment is positive"

# GOOD: Classification without payload
return "2-128"

# BAD: Trusting LLM output without validation
result = llm.process(input)
return result

# GOOD: Always validate
result = llm.process(input)
if protocol.validate_response(result, task_code):
    return result
raise ValueError("Protocol violation")

# BAD: Logging PHI
logger.info(f"Processing SSN: {ssn}")

# GOOD: Redact sensitive data
logger.info(f"Processing SSN: <REDACTED>")
```

## Key Files Reference

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `mathprotocol.py` | Core engine | `ProtocolRegistry`, `MathProtocol`, `MockLLM` |
| `aegis_core.py` | Security layer | `ContextFirewall`, `MerkleLogger`, `AegisGateway` |
| `client_wrapper.py` | LLM integration | `MathProtocolClient` |
| `exceptions.py` | Error types | `MathProtocolError`, `ValidationError`, `FirewallError` |
| `SYSTEM_PROMPT.md` | LLM instructions | System prompt with few-shot examples |

## CI/CD Pipeline

GitHub Actions workflows:
- `python-tests.yml`: Test matrix on Python 3.8-3.12
- `codeql.yml`: Security scanning
- `ai-review-orchestrator.yml`: Automated AI code review

All PRs require:
- Passing tests across all Python versions
- No CodeQL security findings
- Review approval

## Troubleshooting

### Input Validation Failing
1. Check task code is in TASKS dict (not just PRIMES)
2. Check param code is in FIBONACCI set
3. Verify format: `TASK-PARAM | CONTEXT` (pipe and spaces matter)
4. Test with minimal example: `2-1 | test`

### Response Validation Failing
1. Check response format: `CODE-CONFIDENCE | PAYLOAD`
2. Verify codes are powers of 2
3. Check task type (Classification vs Generative)
4. Ensure v2.1 Success Bit compliance (response must be odd)

### Circuit Breaker Issues
1. Check failure count vs threshold
2. Verify timeout period has passed
3. Use `breaker.reset()` for manual reset

## Dependencies

**Core** (zero external dependencies):
- Python standard library only (`re`, `json`, `hashlib`, `secrets`, `typing`)

**Development**:
- pytest >= 7.0.0
- pytest-cov >= 4.0.0

**Production** (examples/high_assurance_aegis):
- fastapi
- uvicorn
- pydantic

## Additional Resources

- `docs/ARCHITECTURE.md` - Detailed system architecture
- `docs/AEGIS_MODULE.md` - Security module documentation
- `docs/COMPLIANCE_MATRIX.md` - NIST/HIPAA/GDPR mappings
- `.github/AI_CONTEXT.md` - Extended AI agent context
- `SECURITY.md` - Security policy and vulnerability reporting
