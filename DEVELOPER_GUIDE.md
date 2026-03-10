# Snowstream CLI Developer Guide

---

## Pull Request Tagging

All PRs **must** be tagged in the title with one of the following keywords:

- `PATCH:` — for bug fixes, minor changes, or documentation updates
- `FEATURE:` — for new features or enhancements
- `BREAKING-CHANGE:` — for changes that break backward compatibility or require major version bump

> These tags will be used for automated versioning and changelog generation.

---

## Docstring Format

All functions, classes, and modules should use the following docstring template:
```
"""
< brief description >

### Inputs
    - name | optional (if applicable) | type (style = `<type=str>`  | <default=`val`>:
          <param description>

### Returns
    `type`

### Raises
    Exception type(s) or None

### Example

# example code block
"""
```

**Sample docstring:**

```
"""
Display a coloured terminal prompt and return a validated user response.

### Inputs
    - prompt `<type=str>`: The message displayed to the user before the input cursor.
    - expected_type (optional) `<type=type>` <default=`str`>:
        The expected type of the response. If the raw input is not of this type, a cast is attempted.
    - expected_values (optional) `<type=list[str] | None>` <default=`None`>:
        Allowlist of valid responses. If the response is not in this list, `InvalidInput` is raised.
    - case (optional) `<type=Callable>` <default=`str.lower`>:
        A string method applied to the raw input before validation (e.g. `str.lower`, `str.upper`).
    - message_type (optional) `<type=MessageType>` <default=`MessageType.INFO`>:
        Controls the colour of the prompt text.

### Returns
    `Any`: The validated and type-coerced user response.

### Raises
    - `InvalidInput`: If the response cannot be coerced to `expected_type`, or if the response is not in `expected_values`.
    - `SnowstreamInternalError`: If `message_type` is not a valid key in the colour options map.

### Example
response = terminal_prompt(
    "Enter your username"
    , expected_type=str
    , expected_values=None
    , case=str.lower
    , message_type=MessageType.INFO
)
"""
```

---

## Code Styling Rules

- Multi-line commas are **prefixed**:

```python
my_dict = {
    "key1": "val1"
    , "key2": "val2"
}
```

- Function and class docstrings must follow the template above.
- Use type hints for all function parameters and return values.
- Prefer explicit imports and avoid wildcard imports.
- Keep lines under 100 characters where possible.
- Group related functions and classes together.
- Add comments for complex logic or non-obvious code.

---

## Testing & CI

- All new code must include unit tests.
- Run `pytest` and `pylint snowstream_cli` locally before submitting a PR.
- CI will run lint, tests, and build on all pushes and PRs.

---

## Example PR Title

- `PATCH: Fix typo in CLI help text`
- `FEATURE: Add support for multiple environments`
- `BREAKING-CHANGE: Refactor project structure`

---

## Additional Notes

- Keep documentation up to date with code changes.
- Use descriptive commit messages.
- Review open issues before starting new work.
