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

## Coding Guidelines
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Document all classes and methods with docstrings
- Validate all inputs against mathematical sets
- Keep validation logic strict and deterministic
- No external dependencies beyond standard library where possible
- Write comprehensive unit tests for all validation logic

## Security Considerations
- Never allow arbitrary code execution
- Validate all inputs strictly against defined mathematical sets
- Sanitize all text payloads
- Log security-relevant events
- Handle errors gracefully without exposing internal details
