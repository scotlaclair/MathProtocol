# GitHub Copilot Instructions for MathProtocol

## Project Overview
MathProtocol is a Python-based system that forces an LLM to communicate using strict mathematical codes. This prevents prompt injection and allows the LLM to function as a logic engine in software pipelines.

## Key Concepts

### Protocol Structure
- **Input Format**: `[TASK]-[PARAM] | [CONTEXT]`
- **Output Format**: `[RESPONSE]-[CONFIDENCE] | [PAYLOAD]`

### Mathematical Sets
1. **Primes (2-97)**: Used for TASKS
2. **Fibonacci (1-89)**: Used for PARAMETERS
3. **Powers of 2 (2-4096)**: Used for RESPONSES

### Task Types
- **Classification Tasks** (Codes 2, 5, 13, 19, 29): NO payload allowed
- **Generative Tasks** (Codes 3, 7, 11, 17, 23): MUST include payload

### Code Mappings
- **Tasks**: 2=Sentiment, 3=Summarization, 5=LangDetect, 7=EntityExtract, 11=Q&A, 13=Classify, 17=Translate, 19=Moderate, 23=Keywords, 29=Readability
- **Params**: 1=Brief, 2=Medium, 3=Detailed, 5=JSON, 8=List, 13=Confidence, 21=Explain
- **Responses**: 2=Positive, 4=Negative, 8=Neutral, 16=English, 32=Spanish, 64=French, 128=HighConf, 256=MedConf, 512=LowConf

### Error Codes
- 1024: Invalid Task
- 2048: Invalid Parameter
- 4096: Invalid Format

## Architecture Overview

### Core Components
- **`mathprotocol.py`**: Protocol engine with `ProtocolRegistry` singleton, `MathProtocol` class, and `MockLLM` for testing
- **`aegis_core.py`**: Security layer with `ContextFirewall`, `MerkleLogger`, and `AegisGateway`
- **`client_wrapper.py`**: LLM API integration for OpenAI/Anthropic clients
- **`examples/high_assurance_aegis/`**: Production FastAPI deployment with security middleware

### Data Flow
1. Input validation against mathematical sets
2. Security sanitization via Aegis components
3. LLM processing with deterministic prompts
4. Response validation with Success Bit requirement
5. Audit logging to Merkle chains

## Critical Developer Workflows

### Testing
```bash
# Run full test suite
pytest test_mathprotocol.py test_aegis_core.py -v

# Run with coverage
pytest --cov=mathprotocol --cov-report=term

# Run built-in protocol tests
python mathprotocol.py

# Run examples
python examples.py
```

### CLI Usage
```bash
# List all registered codes
python mathprotocol_cli.py list

# Compose protocol prompts
python mathprotocol_cli.py compose --task 17 --params 1 2 --context "Hello World"
```

### Development Commands
```bash
# Install dependencies
pip install -e .

# Run FastAPI server example
cd examples/high_assurance_aegis && python server.py
```

## Version 2.1 Success Bit Requirement (CRITICAL)

**All valid response codes MUST be odd numbers** (base power of 2 + 1):

```python
# Valid responses (with Success Bit)
"3-128"    # 2 (Positive) + 1 = 3
"17-128"   # 16 (English) + 1 = 17
"5-256"    # 4 (Negative) + 1 = 5

# Invalid responses (missing Success Bit)
"2-128"    # Even number = protocol failure
"16-128"   # Even number = protocol failure
```

**Validation**: `(response_code & 1) == 1` must be true for all valid responses.

## Security Considerations

### Aegis Security Layer
- **ContextFirewall**: Neutralizes prompt injection patterns
- **MerkleLogger**: Tamper-evident audit logging
- **DataAirlock**: PHI/PII redaction and rehydration
- **CircuitBreaker**: Fault isolation and recovery
- **DeadLetterVault**: Forensic analysis of failures

### Logging Requirements
All security events MUST be logged to Merkle audit chains. Never log raw user input containing PHI/PII.

## Coding Guidelines

### Python Standards
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Document all classes and methods with Google-style docstrings
- Validate all inputs against mathematical sets
- Keep validation logic strict and deterministic
- No external dependencies beyond standard library where possible
- Write comprehensive unit tests for all validation logic

### Protocol Registry Pattern
Use the `ProtocolRegistry` singleton for dynamic code registration:

```python
from mathprotocol import registry

# Register custom codes
registry.register_task(31, "CustomTask")
registry.register_parameter(34, "CustomParam")
```

### Client Integration Pattern
```python
from client_wrapper import MathProtocolClient

client = MathProtocolClient(llm_client, model, system_prompt, provider="openai")
result = client.execute(task_code=2, param_code=1, context="Sample text")
```

## Integration Points

### LLM Providers
- **OpenAI**: `client.chat.completions.create` with temperature=0
- **Anthropic**: `client.messages.create` with temperature=0

### Web Frameworks
- **FastAPI**: Production server example in `examples/high_assurance_aegis/`
- **Middleware**: Honeypot protection and security controls

### Containerization
- **Docker**: Multi-stage build with non-root user
- **Security**: Minimal attack surface, proper file permissions

## Common Patterns

### Input Validation
```python
protocol = MathProtocol()
if protocol.validate_input("2-1 | Sample text"):
    parsed = protocol.parse_input("2-1 | Sample text")
    # parsed = {'task': 2, 'param': 1, 'context': 'Sample text'}
```

### Response Validation
```python
if protocol.validate_response("3-128", task_code=2):  # Classification task
    parsed = protocol.parse_response("3-128")
    # parsed = {'codes': [3, 128], 'payload': ''}
```

### Security Logging
```python
from aegis_core import MerkleLogger

logger = MerkleLogger()
logger.log_event({"event": "security_check", "threat_level": 0})
```

## File Organization

### Core Files
- `mathprotocol.py`: Protocol implementation
- `aegis_core.py`: Security components
- `client_wrapper.py`: API integration
- `exceptions.py`: Custom error classes

### Test Files
- `test_mathprotocol.py`: Protocol unit tests
- `test_aegis_core.py`: Security tests

### Examples & Tools
- `examples.py`: Usage demonstrations
- `mathprotocol_cli.py`: Command-line interface
- `examples/high_assurance_aegis/`: Production deployment

### Documentation
- `docs/ARCHITECTURE.md`: System design
- `docs/AEGIS_MODULE.md`: Security documentation
- `CLAUDE.md`: AI assistant guide
