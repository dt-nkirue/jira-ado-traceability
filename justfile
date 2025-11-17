# Jira-ADO Traceability Development Commands

# Set shell for Windows
set shell := ["pwsh.exe", "-c"]

# Default recipe shows available commands
default:
    @just --list

# Development environment setup
dev-setup:
    uv venv
    uv sync
    @echo "[OK] Development environment ready"

# Run all tests
test:
    uv run pytest tests/

# Run tests with coverage
test-cov:
    uv run pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run only unit tests
test-unit:
    uv run pytest tests/unit/

# Run only integration tests
test-integration:
    uv run pytest tests/integration/

# Run only e2e tests
test-e2e:
    uv run pytest tests/e2e/

# Linting with ruff
lint:
    uv run ruff check src/ tests/

# Fix linting issues automatically
fix:
    uv run ruff check --fix src/ tests/

# Format code with ruff
format:
    uv run ruff format src/ tests/

# Type checking with pyright
typecheck:
    uv run pyright src/

# Check for forbidden noqa comments
check-noqa:
    @powershell -Command "if (rg --type py 'noqa' src/ tests/ scripts/) { Write-Host 'ERROR: noqa comments are forbidden!' -ForegroundColor Red; exit 1 } else { Write-Host '[OK] No noqa comments found' -ForegroundColor Green; exit 0 }"

# Check line counts (max 500 lines per file)
check-cloc:
    uv run python scripts/check_line_counts.py

# Full quality check (noqa check + lint + typecheck + line counts)
check: check-noqa lint typecheck check-cloc
    @echo "[OK] All quality checks passed"

# Run code quality checks and formatting (use after changes)
dev: format check
    @echo "[OK] Code formatted and all checks passed"

# Clean build artifacts
clean:
    @powershell -Command "if (Test-Path build) { Remove-Item -Path build -Recurse -Force }"
    @powershell -Command "if (Test-Path dist) { Remove-Item -Path dist -Recurse -Force }"
    @powershell -Command "Get-ChildItem -Path . -Filter '*.egg-info' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    @powershell -Command "if (Test-Path .pytest_cache) { Remove-Item -Path .pytest_cache -Recurse -Force }"
    @powershell -Command "if (Test-Path .coverage) { Remove-Item -Path .coverage -Force }"
    @powershell -Command "if (Test-Path htmlcov) { Remove-Item -Path htmlcov -Recurse -Force }"
    @powershell -Command "Get-ChildItem -Path . -Include __pycache__ -Recurse -Force -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    @echo "[OK] Cleaned build artifacts"

# Build distribution packages
build: clean
    uv build
    @echo "[OK] Built distribution packages"

# Run the traceability report (manual mode)
run-manual:
    uv run python src/jira_ado_traceability/cli_manual.py

# Run the traceability report (scheduled mode)
run-scheduled:
    uv run python src/jira_ado_traceability/cli_scheduled.py

# Generate report with custom config
run-config config_file:
    uv run python src/jira_ado_traceability/cli_scheduled.py --config {{config_file}}
