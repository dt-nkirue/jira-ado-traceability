# CLAUDE.md - AI Assistant Rules for Jira-ADO Traceability

## PROJECT CONTEXT

This is a Jira-ADO Traceability System that generates comprehensive reports between Jira issues and Azure DevOps work items. This project uses the DataTorque Python template with `uv`, `just`, strict linting, and type checking.

## STRICT RULES - MUST ALWAYS FOLLOW

### Environment Rules
1. **ALWAYS use `uv` for Python operations** - **NEVER** use system Python
2. **ALWAYS use `just` commands** for all project operations (test, lint, format, check)
3. **ALWAYS use bash for command-line operations** - **NEVER** use `cmd`
4. **Use PowerShell ONLY for Windows-specific justfile recipes**

### Code Quality Rules
1. **Maximum file length: 500 lines** - NO EXCEPTIONS
2. **Maximum function length: 50 lines** - NO EXCEPTIONS
3. **NEVER use `# noqa` comments** - ALL linting issues MUST be resolved
4. **ALWAYS use strict typing** - no `Any` types without explicit justification
5. **Follow SRP (Single Responsibility Principle)** - each module/function does ONE thing
6. **Follow DRY (Don't Repeat Yourself)** - extract common patterns into utilities
7. **ALL code must pass `just check`** before completion

### Testing Rules
1. **Run `just format` then `just check` after EVERY code change**
2. **Run `just test` to verify functionality**
3. **Create unit tests for all new modules**
4. **Maintain test coverage above 70%**

### Git Commit Rules (CRITICAL)
- **NEVER annotate git commits with Claude Code as author**
- **NEVER add Co-Authored-By: Claude or similar attributions**
- **NEVER mention "Generated with Claude Code" in commit messages**
- All commits should appear as if written by the human developer
- Use conventional commit format: `type: description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`

### Key Commands
```bash
# Setup environment
just dev-setup

# Quality checks (MUST PASS)
just format       # Format code first
just check        # Run all checks (lint + typecheck + cloc)
just lint         # Linting only
just typecheck    # Type checking only
just fix          # Auto-fix linting issues

# Testing
just test         # Run all tests
just test-cov     # With coverage
just test-unit    # Unit tests only

# Running the tool
just run-manual     # Run with hardcoded config
just run-scheduled  # Run with config file

# Build
just build        # Create distribution
just clean        # Clean artifacts
```

### Development Workflow
1. Analyze existing code structure
2. Create implementation plan
3. Implement changes incrementally
4. Run `just format` to format code
5. Run `just check` to verify quality (must pass)
6. Ensure all tests pass with `just test`
7. Verify output matches expectations

## PROJECT STRUCTURE

```
jira-ado-traceability-project/
├── src/jira_ado_traceability/
│   ├── __init__.py
│   ├── models.py            # Data models (TypedDicts, dataclasses)
│   ├── config.py            # Configuration management
│   ├── jira_parser.py       # Parse Jira issues
│   ├── ado_client.py        # ADO API client
│   ├── fuzzy_matcher.py     # Fuzzy matching logic
│   ├── comparator.py        # Comparison functions
│   ├── reporter.py          # Summary statistics
│   ├── excel_generator.py   # Excel report generation
│   ├── cli_manual.py        # Manual mode CLI
│   └── cli_scheduled.py     # Scheduled mode CLI
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── scripts/
│   └── check_line_counts.py
├── pyproject.toml          # Project configuration
├── justfile                # Build automation
├── .pre-commit-config.yaml # Pre-commit hooks
└── README.md              # Documentation
```

## MODULAR ARCHITECTURE

The codebase is organized into focused modules:

1. **models.py**: Data structures (JiraIssue, AdoWorkItem, FuzzyMatch, Config)
2. **config.py**: Configuration loading from files or environment
3. **jira_parser.py**: Load and parse Jira JSON data
4. **ado_client.py**: Azure DevOps API interactions
5. **fuzzy_matcher.py**: Fuzzy text matching for unlinked items
6. **comparator.py**: Compare status, severity, assignee
7. **reporter.py**: Generate summary statistics
8. **excel_generator.py**: Create multi-sheet Excel reports
9. **cli_manual.py**: Entry point for manual mode
10. **cli_scheduled.py**: Entry point for scheduled mode

## CONFIGURATION

The tool supports two modes:

### Manual Mode (cli_manual.py)
- Hardcoded configuration in the script
- For quick testing and development
- Run with: `just run-manual`

### Scheduled Mode (cli_scheduled.py)
- Loads configuration from config.json
- Environment variable support for credentials
- For production/automation
- Run with: `just run-scheduled`

## CRITICAL REMINDERS

1. **NO files over 500 lines** - Split into modules
2. **NO functions over 50 lines** - Extract sub-functions
3. **NO `# noqa` comments** - Fix the actual issues
4. **ALWAYS use `uv run`** for Python commands
5. **ALWAYS use `just`** for project commands
6. **ALWAYS add type hints** to all functions
7. **Test changes thoroughly** before committing

## SECURITY

- Never hardcode credentials in source files
- Use environment variables for sensitive data
- Keep `.env` and `config.json` out of version control
- Pre-commit hooks scan for secrets with gitleaks

## TESTING

- Write unit tests for all new functions
- Test error handling paths
- Verify output format matches expectations
- Run full test suite before committing

## DOCUMENTATION

- Update README when adding features
- Add docstrings to all functions (Google style)
- Document configuration options
- Include usage examples
