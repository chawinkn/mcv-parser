```markdown
# mcv-parser Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and conventions used in the `mcv-parser` Python codebase. You'll learn how to implement new features, update dependencies, and maintain documentation following the repository's established workflows and coding standards. The guide covers file naming, import/export styles, commit patterns, and provides step-by-step instructions for common development tasks.

## Coding Conventions

### File Naming
- **Style:** camelCase
- **Example:** `parseFile.py`, `mainParser.py`

### Import Style
- **Style:** Relative imports
- **Example:**
  ```python
  from .utils import parseConfig
  ```

### Export Style
- **Style:** Named exports (explicitly listing exported functions/classes)
- **Example:**
  ```python
  __all__ = ['parseFile', 'validateInput']
  ```

### Commit Patterns
- **Type:** Conventional commits
- **Prefixes:** `feat`, `fix`, `docs`
- **Example:**
  ```
  feat: add support for new config format
  fix: correct parsing of edge cases
  docs: update usage section in README
  ```
- **Average commit message length:** 28 characters

## Workflows

### Feature Implementation: Main & mcv
**Trigger:** When adding or enhancing a core feature that requires changes to both the main entry point (`main.py`) and the core logic (`mcv.py`).
**Command:** `/add-feature-main-mcv`

1. Edit `main.py` to add or update CLI/entry logic.
   ```python
   # main.py
   from .mcv import parseFile

   def main():
       # new CLI argument handling
       ...
   ```
2. Edit `mcv.py` to implement or adjust core functionality.
   ```python
   # mcv.py
   def parseFile(filename):
       # new parsing logic
       ...
   ```
3. Optionally update dependencies or supporting files (`pyproject.toml`, `poetry.lock`, `.gitignore`).

---

### Dependency or Configuration Update
**Trigger:** When adding a feature that requires new dependencies or updating project configuration.
**Command:** `/update-dependencies`

1. Edit `pyproject.toml` to add or update dependencies.
   ```toml
   [tool.poetry.dependencies]
   new-package = "^1.2.3"
   ```
2. Regenerate `poetry.lock` to lock dependency versions:
   ```sh
   poetry lock
   ```

---

### README Update
**Trigger:** When adding a new feature or clarifying documentation.
**Command:** `/update-readme`

1. Edit `README.md` to add or update documentation.
   ```markdown
   ## New Feature
   Describe how to use the new feature here.
   ```

## Testing Patterns

- **Framework:** Unknown (not explicitly detected)
- **File Pattern:** Files named with `*.test.*` (e.g., `parser.test.py`)
- **Example:**
  ```python
  # parser.test.py
  from .mcv import parseFile

  def test_parseFile_valid():
      assert parseFile('valid.mcv') == expected_output
  ```
- **Tip:** Place test files alongside the code they test, using the `.test.` naming convention.

## Commands

| Command                  | Purpose                                                      |
|--------------------------|--------------------------------------------------------------|
| /add-feature-main-mcv    | Implement or enhance a feature involving main.py and mcv.py  |
| /update-dependencies     | Update dependencies or configuration files                   |
| /update-readme           | Add or update documentation in README.md                     |
```