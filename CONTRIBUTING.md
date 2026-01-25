# Contributing to MathProtocol

Thank you for your interest in contributing to MathProtocol! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs
- Use the GitHub issue tracker
- Describe the bug in detail
- Include steps to reproduce
- Provide expected vs actual behavior
- Include your Python version and OS

### Suggesting Enhancements
- Use the GitHub issue tracker
- Clearly describe the enhancement
- Explain why it would be useful
- Provide examples if possible

### Pull Requests
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass
6. Update documentation
7. Commit your changes (`git commit -m 'Add some feature'`)
8. Push to the branch (`git push origin feature/your-feature`)
9. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/scotlaclair/MathProtocol.git
cd MathProtocol

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest
```

## Coding Standards

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for all classes and functions
- Keep functions focused and small
- Write comprehensive tests
- Maintain backward compatibility when possible

## Mathematical Protocol Rules

When contributing to the protocol logic:
- Maintain strict validation against the three mathematical sets (Primes, Fibonacci, Powers of 2)
- Never allow inputs outside defined ranges
- Preserve deterministic behavior
- Document any changes to code mappings
- Ensure error codes remain consistent

## Testing

- Write unit tests for all new features
- Ensure all tests pass before submitting PR
- Aim for high code coverage
- Test edge cases and error conditions

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Keep SYSTEM_PROMPT.md in sync with code

## Questions?

Feel free to open an issue for questions or discussion about contributing.
