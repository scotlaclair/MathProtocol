# MathProtocol AI Context

This file serves as the master reference for all AI agents working on the MathProtocol repository. It defines immutable laws, protocol specifications, and development guidelines.

## Repository Laws (Immutable)

These rules **MUST NEVER** be violated by any code change:

### 1. Mathematical Determinism
- **Law**: TASK codes must be prime numbers from the defined set
- **Law**: PARAM codes must be Fibonacci numbers from the defined set
- **Law**: RESPONSE codes must be powers of 2 from the defined set
- **Rationale**: Mathematical sets provide deterministic validation

### 2. Task Type Safety
- **Law**: Classification tasks (2, 5, 13, 19, 29) MUST NOT have payload
- **Law**: Generative tasks (3, 7, 11, 17, 23) MUST have payload
- **Rationale**: Type safety prevents protocol violations

### 3. Zero Natural Language in Control Flow
- **Law**: TASK and PARAM must be mathematical codes, never natural language
- **Law**: Only CONTEXT field may contain natural language
- **Rationale**: Prevents prompt injection

### 4. Security Event Logging
- **Law**: All security events MUST be logged to Merkle Audit Chain
- **Law**: Failed transactions MUST be stored in Dead Letter Vault
- **Rationale**: Forensic survivability and compliance

### 5. PHI/PII Protection
- **Law**: Sensitive data MUST be redacted before LLM processing
- **Law**: DataAirlock MUST scan for: EMAIL, SSN, MRN, PHONE, CREDIT_CARD
- **Rationale**: HIPAA and GDPR compliance

## Protocol Specification

### Valid Task Codes (Primes)

```python
TASKS = {
    2: "Sentiment",       # Classification
    3: "Summarization",   # Generative
    5: "LangDetect",      # Classification
    7: "EntityExtract",   # Generative
    11: "Q&A",            # Generative
    13: "Classify",       # Classification
    17: "Translate",      # Generative
    19: "Moderate",       # Classification
    23: "Keywords",       # Generative
    29: "Readability"     # Classification
}
```

### Valid Parameter Codes (Fibonacci)

```python
PARAMS = {
    1: "Brief",
    2: "Medium",
    3: "Detailed",
    5: "JSON",
    8: "List",
    13: "Confidence",
    21: "Explain"
}
```

### Valid Response Codes (Powers of 2)

```python
RESPONSES = {
    2: "Positive",
    4: "Negative",
    8: "Neutral",
    16: "English",
    32: "Spanish",
    64: "French",
    128: "HighConf",
    256: "MedConf",
    512: "LowConf",
    1024: "InvalidTask",
    2048: "InvalidParam",
    4096: "InvalidFormat"
}
```

### Trap Codes (Honeypots)

**DO NOT ASSIGN THESE CODES TO TASKS**

These primes are reserved as honeypot traps for intrusion detection:
```
43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
```

If a client uses these codes, they are immediately banned. This is intentional for security.

### Canary Parameters

These Fibonacci numbers are rarely used and serve as sophisticated probe detection:
```
34, 55
```

## AEGIS Security Architecture

### Defense Layers (In Order)

1. **API Gateway (Nginx)**
   - TLS termination
   - Rate limiting
   - Basic WAF rules

2. **Honeypot Middleware**
   - Trap code detection
   - Immediate IP banning
   - Attack logging

3. **DataAirlock**
   - PHI/PII redaction (inbound)
   - Token generation
   - Rehydration (outbound)

4. **Protocol Validator**
   - Input format validation
   - Code set membership checks
   - Task/param validity

5. **Circuit Breaker**
   - Failure rate tracking
   - State management (CLOSED/OPEN/HALF_OPEN)
   - Resource protection

6. **Logic Engine (LLM)**
   - Process sanitized input only
   - Return protocol-compliant output
   - No direct external access

7. **Response Validator**
   - Output format validation
   - Task type checking
   - Code validity

8. **Merkle Audit Chain**
   - Batch event logging
   - Cryptographic chaining
   - Tamper detection

9. **Dead Letter Vault**
   - Failed transaction storage
   - Full context preservation
   - Forensic replay capability

### Security Control Mappings

| Component | NIST Control | HIPAA | OWASP LLM |
|-----------|-------------|-------|-----------|
| DataAirlock | SC-8 | § 164.312(e)(1) | LLM06 |
| Honeypot | SI-4 | § 164.308(a)(5)(ii)(C) | N/A |
| Circuit Breaker | SC-5, SC-7 | § 164.312(a)(1) | LLM04 |
| Merkle Chain | AU-9, AU-10 | § 164.312(b) | N/A |
| Dead Letter Vault | AU-11 | § 164.312(b) | LLM09 |
| Protocol Validator | SI-10 | § 164.312(c)(1) | LLM01 |

## Code Style Guidelines

### Python

**Style**: PEP 8 compliant
- Max line length: 100 characters
- Indentation: 4 spaces
- Quotes: Double quotes for strings

**Type Hints**: Required for all functions
```python
def process_request(input_str: str) -> Dict[str, Any]:
    pass
```

**Docstrings**: Required (Google style)
```python
def validate_input(self, input_str: str) -> bool:
    """
    Validate if input matches the format: [TASK]-[PARAM] | [CONTEXT]
    
    Args:
        input_str: The input string to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    pass
```

**Imports**: Organize as
1. Standard library
2. Third-party
3. Local modules

### Security Code Comments

All security-critical code must reference the control it implements:

```python
class DataAirlock:
    """
    Implements HIPAA-compliant PHI/PII redaction.
    
    Security Control: HIPAA § 164.514(b) - De-identification
    """
    pass
```

### Testing

**Coverage**: Minimum 80% for security modules

**Structure**:
- Unit tests: Test individual functions
- Integration tests: Test module interactions
- Security tests: Test attack scenarios

**Naming**: `test_<function>_<scenario>`
```python
def test_validate_input_with_valid_format():
    pass

def test_validate_input_with_invalid_task():
    pass
```

## Development Workflow

### Before Making Changes

1. Read relevant documentation (ARCHITECTURE.md, COMPLIANCE_MATRIX.md)
2. Check for related issues or PRs
3. Review existing tests
4. Understand security implications

### Making Changes

1. **Minimal Changes**: Change only what's necessary
2. **Security First**: Never weaken security for convenience
3. **Test Thoroughly**: Add tests for new behavior
4. **Document**: Update docs if behavior changes
5. **No Secrets**: Never commit API keys, passwords, etc.

### After Making Changes

1. Run tests: `pytest test_mathprotocol.py -v`
2. Check coverage: `pytest --cov=mathprotocol --cov-report=term`
3. Lint code: `black mathprotocol.py` (if black is available)
4. Verify no PHI/PII in logs
5. Run security validation: `python examples/high_assurance_aegis/aegis_core.py`

## Common Patterns

### Input Validation

```python
def validate_input(self, input_str: str) -> bool:
    # 1. Check basic format
    if not input_str or not isinstance(input_str, str):
        return False
    
    # 2. Match regex
    pattern = r'^(\d+)-(\d+)(\s*\|\s*.+)?$'
    match = re.match(pattern, input_str)
    if not match:
        return False
    
    # 3. Extract codes
    task = int(match.group(1))
    param = int(match.group(2))
    
    # 4. Validate against sets
    if task not in self.PRIMES or task not in self.TASKS:
        return False
    if param not in self.FIBONACCI:
        return False
    
    return True
```

### Response Validation

```python
def validate_response(self, response_str: str, task_code: int) -> bool:
    parsed = self.parse_response(response_str)
    codes = parsed["codes"]
    payload = parsed["payload"]
    
    # Check error codes
    if len(codes) == 1 and codes[0] in {1024, 2048, 4096}:
        return payload == ""
    
    # Check normal responses
    if len(codes) != 2:
        return False
    
    # Validate task type requirements
    if task_code in self.CLASSIFICATION_TASKS:
        return payload == ""
    elif task_code in self.GENERATIVE_TASKS:
        return payload != ""
    
    return True
```

### PHI Redaction

```python
def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
    redacted = text
    token_map = {}
    
    for pattern_name, pattern in self.PATTERNS.items():
        matches = re.findall(pattern, text)
        for match in matches:
            # Generate token
            token = f"<{pattern_name}_{counter}>"
            
            # Store mapping
            token_map[token] = match
            
            # Replace in text
            redacted = redacted.replace(match, token)
    
    return redacted, token_map
```

## Anti-Patterns (Avoid These)

### ❌ Natural Language in Protocol

```python
# BAD
task = "sentiment analysis"  # Natural language
param = "brief mode"

# GOOD
task = 2  # Prime number
param = 1  # Fibonacci number
```

### ❌ Payload in Classification

```python
# BAD
return "2-128 | The sentiment is positive"  # Classification with payload

# GOOD
return "2-128"  # Classification without payload
```

### ❌ No Payload in Generative

```python
# BAD
return "16-128"  # Translation without payload

# GOOD
return "32-128 | Hola Mundo"  # Translation with payload
```

### ❌ Logging PHI

```python
# BAD
logger.info(f"Processing patient SSN: {ssn}")

# GOOD
logger.info(f"Processing patient SSN: <REDACTED>")
```

### ❌ Trusting LLM Output

```python
# BAD
result = llm.process(input)
return result  # Not validated

# GOOD
result = llm.process(input)
if protocol.validate_response(result, task_code):
    return result
else:
    raise ValueError("Invalid response")
```

## Testing Strategy

### Unit Tests

Test individual components in isolation:
- MathProtocol validation methods
- DataAirlock redaction/rehydration
- Circuit Breaker state transitions
- Merkle Chain root computation

### Integration Tests

Test component interactions:
- Full request pipeline (Gateway → LLM → Response)
- Security layer coordination
- Error propagation

### Security Tests

Test attack scenarios:
- Prompt injection attempts
- Honeypot triggering
- PHI leakage detection
- Response validation bypass attempts

### Performance Tests

Test under load:
- Request throughput
- Latency percentiles
- Memory usage
- Circuit breaker behavior under stress

## Dependencies

### Core (No External Dependencies)

MathProtocol core (`mathprotocol.py`) uses **only Python standard library**:
- `re` - Regular expressions
- `typing` - Type hints

This ensures maximum portability and minimal attack surface.

### AEGIS Module (Production)

```
fastapi - Web framework
uvicorn - ASGI server
pydantic - Data validation
```

### Development & Testing

```
pytest - Testing framework
pytest-cov - Coverage reports
black - Code formatting (optional)
```

## Troubleshooting

### Issue: Input Validation Failing

**Symptoms**: Valid-looking input rejected

**Debug Steps**:
1. Check task code is in TASKS dict (not just PRIMES)
2. Check param code is in FIBONACCI set
3. Verify format: `TASK-PARAM | CONTEXT` (pipe and spaces matter)
4. Test with minimal example: `2-1 | test`

### Issue: Response Validation Failing

**Symptoms**: LLM response rejected

**Debug Steps**:
1. Check response format: `CODE-CONFIDENCE | PAYLOAD`
2. Verify codes are powers of 2
3. Check task type: Classification vs Generative
4. Ensure payload presence matches task type

### Issue: PHI Leaking

**Symptoms**: Sensitive data in logs or LLM output

**Debug Steps**:
1. Verify DataAirlock redaction is enabled
2. Check PATTERNS regex covers all PHI types
3. Ensure rehydration only happens at network edge
4. Review audit logs for PHI strings

### Issue: Circuit Breaker Stuck Open

**Symptoms**: All requests failing with 503

**Debug Steps**:
1. Check failure count vs threshold
2. Verify timeout period has passed
3. Try manual reset: `breaker.reset()`
4. Investigate root cause of LLM failures

## Release Process

### Pre-Release Checklist

- [ ] All tests passing
- [ ] Security validation passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped in `setup.py`
- [ ] No secrets in code
- [ ] Dependencies pinned

### Versioning

Follow Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes (e.g., protocol format change)
- **MINOR**: New features (e.g., new task type)
- **PATCH**: Bug fixes (e.g., regex improvement)

Example: `1.2.3` = Major 1, Minor 2, Patch 3

### Security Releases

For security fixes:
1. Fix vulnerability in private branch
2. Prepare security advisory
3. Release fix and advisory simultaneously
4. Notify users via GitHub Security Advisory

## Contact

For questions or clarifications:
- Security issues: security@mathprotocol.org
- General questions: Create a GitHub issue
- Agent feedback: Comment on relevant PR

---

*Last Updated: January 2024*
*Document Version: 1.0*
*Authoritative Source for All AI Agents*
