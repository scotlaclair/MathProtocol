# Contributing to MathProtocol

## Pull Request Review Process

### Review Response Requirements

When addressing review comments, contributors and automated reviewers MUST:

1. **Reply to each comment** - Every review comment must receive a direct response
2. **Indicate resolution status** - Use one of these formats:
   - ✅ **Addressed in commit `<sha>`** - Changes made as suggested
   - 💬 **Discussion needed** - Comment requires clarification
   - ❌ **Won't fix** - Explain why suggestion won't be implemented
   - 🔄 **Alternative approach** - Describe different solution

3. **Link to changes** - When code is modified, reference:
   - Commit SHA where change was made
   - Line numbers of modified code
   - Related test updates

### Example Response Format

```markdown
✅ Addressed in commit abc1234

Changed validation from `len(codes) < 2` to `len(codes) != 2` as suggested.
Updated tests in test_mathprotocol.py:L45-L52.
```

### Review Comment Template

Reviewers SHOULD structure comments as:

**Priority**: `P0` (blocking) | `P1` (important) | `P2` (nice-to-have)

**Issue**: [Clear description of the problem]

**Suggested fix**: [Concrete recommendation or code suggestion]

**Why**: [Rationale for the change]

### Automated Reviewer Requirements

Automated review systems (Copilot, Codex, etc.) MUST:

- Post a **summary comment** linking to all addressed items
- Use threaded replies to track resolution
- Mark conversations as "Resolved" when changes are merged
- Provide commit references in responses

## Code Review Checklist

Before marking a PR as ready for merge:

- [ ] All review comments have responses
- [ ] Blocking (P0) issues are resolved
- [ ] Tests pass for all changes
- [ ] Documentation updated if needed
- [ ] Conversations marked as resolved

## For Maintainers

### Merging PRs

Only merge when:
1. All conversations are resolved or have "Won't fix" rationale
2. CI/CD passes
3. At least one approving review (for external contributors)

### Resolving Conversations

**Important**: GitHub Copilot and other automated reviewers cannot automatically resolve their own conversations. The PR author or maintainers must:

1. Verify the fix has been implemented
2. Check the commit reference provided in the response
3. Manually click "Resolve conversation" on each addressed comment

## Protocol-Specific Guidelines

### Validation Changes

When modifying validation logic in `mathprotocol.py`:
- Add corresponding test cases in `test_mathprotocol.py`
- Update examples in `examples.py` if behavior changes
- Document changes in docstrings

### Adding New Task/Response Codes

1. Update the appropriate constant set (PRIMES, FIBONACCI, POWERS_OF_2)
2. Add mapping in TASKS, PARAMS, or RESPONSES dict
3. Update README.md with new code documentation
4. Add test coverage for the new code
5. Update SYSTEM_PROMPT.md if LLM behavior changes

### Error Handling

All error codes must:
- Be powers of 2 >= 1024
- Appear standalone (no confidence or payload)
- Have clear documentation in README.md

## Testing Requirements

All PRs must include:
- Unit tests for new functionality
- Updated tests for modified behavior
- All existing tests must pass
- `pytest -v` must run successfully

## Documentation

Update the following when making changes:
- `README.md` - User-facing documentation
- `SYSTEM_PROMPT.md` - LLM instructions (if protocol changes)
- Docstrings in code
- `examples.py` - Usage examples

## Questions?

Open an issue or start a discussion if you need clarification on these guidelines.