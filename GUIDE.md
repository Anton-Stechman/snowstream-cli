# Snowstream CLI Developer Guide


___
## Versioning

Snowstream CLI uses **semantic versioning** in the format:

    [major].[minor].[patch]

- **Major**: Incremented for breaking changes or major new features (e.g., `BREAKING-CHANGE:` PR tag).
- **Minor**: Incremented for new features or enhancements (e.g., `FEATURE:` PR tag).
- **Patch**: Incremented for bug fixes, minor changes, or documentation updates (e.g., `PATCH:` PR tag).

Version numbers are updated automatically based on PR tags and changelog entries. Always tag your PRs correctly to ensure proper versioning.

___
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

- CLI Operations:
    - CLI command handlers should be in `snowstream_cli._cli._handlers`
    - They should have a dedicated function i.e., `run`
    - Should be a `Generator` function which yields a `tuple`: (`str`, `MessageType`)
    - All CLI commands must be registered in `main.py` as subparsers

- Terminal Output:
    - All terminal output must go through `terminal_print` or `terminal_prompt`
    - Never use `print()` directly outside of `_backend.py`
    - Always pass `MessageType` enum values — never raw strings (e.g. `MessageType.INFO` not `"info"`)

- Generators:
    - All CLI handlers must be generators
    - Generators must yield `tuple[str, MessageType]`
    - Always use `yield from` when delegating to a sub-generator
    - Always `return` after a terminal error yield to stop the generator

- Error Handling:
    - Raise `ValueError` for missing or invalid function arguments
    - Raise `DirectoryNotFoundError` for missing directories when `auto_create=False`
    - Raise `SnowstreamInternalError` for unexpected internal state
    - Raise `InvalidInput` for invalid user input
    - Wrap `KeyError` access on required fields in `try/except` and yield a clean error message

- File Operations:
    - Use `get_file()` for internal package files (templates etc.)
    - Use `get_file(..., internal=False)` for user project files
    - Use `save_file()` for all file writes
    - Use `os.path.join()` for path construction — never string concatenation
    - Use `dir_exists()` and `file_exists()` for path validation — never `os.path.exists()` directly

- Naming Conventions:
    - Private inner functions use double underscore prefix: `__parse_app`
    - Constants are `UPPER_SNAKE_CASE`
    - Enums are `PascalCase` with `UPPER_SNAKE_CASE` members

- Docstrings:
    - All functions and classes must have a docstring following the project template
    - Inner/private functions are exempt from docstrings
    - Docstrings must stay in sync with the actual function signature

- General:
    - Function and class docstrings must follow the template above
    - Use type hints for all function parameters and return values
    - Prefer explicit imports and **NO** wildcard imports (except for `__init__.py`)
    - Keep lines under 100 characters where possible
    - Group related functions and classes together
    - Add comments for complex logic or non-obvious code
    - Never shadow built-in names (e.g. use `project_dir` not `dir`)
    - Use `os.getcwd()` as the default directory fallback — never hardcode paths

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
