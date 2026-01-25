# MathProtocol

A Python-based deterministic LLM control protocol that uses strict mathematical codes to prevent prompt injection and enable LLMs to function as reliable logic engines in software pipelines.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MathProtocol forces Large Language Models (LLMs) to communicate using predefined mathematical codes from three sets:
- **Prime numbers (2-97)**: For TASKS
- **Fibonacci numbers (1-89)**: For PARAMETERS  
- **Powers of 2 (2-4096)**: For RESPONSES and CONFIDENCE

This approach:
- ✅ Prevents prompt injection attacks
- ✅ Ensures deterministic behavior
- ✅ Enables reliable integration in software pipelines
- ✅ Provides clear validation and error handling

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/scotlaclair/MathProtocol.git
cd MathProtocol

# Install (optional)
pip install -e .

# Or just use the mathprotocol.py file directly
```

### Basic Usage

```python
from mathprotocol import MathProtocol, MockLLM

# Initialize
protocol = MathProtocol()
mock_llm = MockLLM()

# Validate input
input_str = "2-1 | This product is amazing!"
if protocol.validate_input(input_str):
    # Process through LLM
    response = mock_llm.process(input_str)
    print(response)  # Output: 2-128 (Positive, High Confidence)
    
    # Parse response
    parsed = protocol.parse_response(response)
    print(parsed)  # {'codes': [2, 128], 'payload': ''}
```

### Running Tests

```bash
# Run the built-in test suite
python mathprotocol.py

# Or with pytest (if installed)
pytest test_mathprotocol.py -v
```

## Protocol Specification

### Input Format
```
[TASK]-[PARAM] | [CONTEXT]
```
- `TASK`: Prime number (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
- `PARAM`: Fibonacci number (1, 2, 3, 5, 8, 13, 21)
- `CONTEXT`: Text to process (optional, but pipe is mandatory if provided)

### Output Format
```
[RESPONSE]-[CONFIDENCE] | [PAYLOAD]
```
- `RESPONSE`: Power of 2 indicating result type
- `CONFIDENCE`: Power of 2 (128=High, 256=Med, 512=Low)
- `PAYLOAD`: Text output (only for generative tasks)

### Task Types

**Classification Tasks** (No payload):
- `2`: Sentiment Analysis
- `5`: Language Detection
- `13`: Classification
- `19`: Content Moderation
- `29`: Readability Analysis

**Generative Tasks** (Requires payload):
- `3`: Summarization
- `7`: Entity Extraction
- `11`: Question Answering
- `17`: Translation
- `23`: Keyword Extraction

### Code Mappings

#### Parameters (Fibonacci)
| Code | Meaning |
|------|---------|
| 1 | Brief |
| 2 | Medium |
| 3 | Detailed |
| 5 | JSON format |
| 8 | List format |
| 13 | Include confidence |
| 21 | Explain reasoning |

#### Responses (Powers of 2)
| Code | Meaning |
|------|---------|
| 2 | Positive |
| 4 | Negative |
| 8 | Neutral |
| 16 | English |
| 32 | Spanish |
| 64 | French |
| 128 | High Confidence |
| 256 | Medium Confidence |
| 512 | Low Confidence |

#### Error Codes
| Code | Meaning |
|------|---------|
| 1024 | Invalid Task |
| 2048 | Invalid Parameter |
| 4096 | Invalid Format |

## Examples

### Example 1: Sentiment Analysis
```python
input_str = "2-1 | This product is terrible!"
response = mock_llm.process(input_str)
# Output: "4-128" (Negative, High Confidence)
```

### Example 2: Translation
```python
input_str = "17-1 | Hello World"
response = mock_llm.process(input_str)
# Output: "32-128 | Hola Mundo" (Spanish, High Confidence)
```

### Example 3: Language Detection
```python
input_str = "5-1 | Bonjour le monde"
response = mock_llm.process(input_str)
# Output: "64-128" (French, High Confidence, No payload)
```

### Example 4: Error Handling
```python
input_str = "4-1 | Some text"
response = mock_llm.process(input_str)
# Output: "1024" (Invalid Task - 4 is not in prime set)
```

## API Reference

### MathProtocol Class

#### `validate_input(input_str: str) -> bool`
Validates if input matches the protocol format and uses valid codes.

#### `parse_input(input_str: str) -> Optional[Dict]`
Parses a valid input into task, param, and context components.

#### `parse_response(response_str: str) -> Dict`
Parses LLM response into codes and payload.

#### `validate_response(response_str: str, task_code: int) -> bool`
Validates if response matches protocol rules for the given task.

### MockLLM Class

#### `process(input_str: str) -> str`
Simulates LLM behavior for testing without requiring an actual LLM API.

## Integration with Real LLMs

To use MathProtocol with a real LLM (OpenAI, Anthropic, etc.):

1. Use the system prompt from `SYSTEM_PROMPT.md`
2. Validate user inputs with `MathProtocol.validate_input()`
3. Send validated inputs to your LLM
4. Parse responses with `MathProtocol.parse_response()`
5. Validate responses with `MathProtocol.validate_response()`

Example with OpenAI:
```python
import openai
from mathprotocol import MathProtocol

protocol = MathProtocol()

# Read system prompt
with open('SYSTEM_PROMPT.md', 'r') as f:
    system_prompt = f.read()

def query_llm(user_input: str) -> str:
    # Validate input
    if not protocol.validate_input(user_input):
        return "4096"  # Invalid format
    
    # Query LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    
    llm_output = response.choices[0].message.content
    
    # Validate response
    parsed = protocol.parse_input(user_input)
    if parsed and protocol.validate_response(llm_output, parsed['task']):
        return llm_output
    else:
        return "4096"  # Protocol violation
```

## Security

MathProtocol is designed to prevent prompt injection by:
- Enforcing strict mathematical validation on all inputs
- Requiring exact format matching
- Ignoring any instructions in the context field that contradict the protocol
- Using deterministic code mappings

See [SECURITY.md](SECURITY.md) for more details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use MathProtocol in your research or project, please cite:

```bibtex
@software{mathprotocol2024,
  author = {LaClair, Scott},
  title = {MathProtocol: Deterministic LLM Control Protocol},
  year = {2024},
  url = {https://github.com/scotlaclair/MathProtocol}
}
```

## Support

- 📖 Documentation: See [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) for detailed protocol specification
- 🐛 Issues: [GitHub Issues](https://github.com/scotlaclair/MathProtocol/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/scotlaclair/MathProtocol/discussions)
