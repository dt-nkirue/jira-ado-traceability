"""Check that no Python file exceeds 500 lines."""

import io
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def check_line_counts(src_dir: Path, max_lines: int = 500) -> bool:
    """Check all Python files in src directory for line count violations.

    Args:
        src_dir: Source directory to check
        max_lines: Maximum allowed lines per file

    Returns:
        True if all files pass, False if any violations
    """
    violations = []

    for py_file in src_dir.rglob("*.py"):
        # Skip __pycache__ directories
        if "__pycache__" in str(py_file):
            continue

        lines = py_file.read_text(encoding="utf-8").splitlines()
        line_count = len(lines)

        if line_count > max_lines:
            violations.append((py_file, line_count))
            print(f"FAIL {py_file.relative_to(src_dir)}: {line_count} lines (exceeds {max_lines})")
        else:
            print(f"PASS {py_file.relative_to(src_dir)}: {line_count} lines")

    if violations:
        print(f"\nFound {len(violations)} files exceeding {max_lines} lines:")
        for file, count in violations:
            print(f"  - {file.relative_to(src_dir)}: {count} lines")
        return False
    else:
        print(f"\nAll Python files are under {max_lines} lines")
        return True


def main() -> None:
    """Run line count checks."""
    # Script is in scripts/, src is in parent directory
    src_dir = Path(__file__).parent.parent / "src"

    if not check_line_counts(src_dir):
        print("\nLine count check FAILED")
        print("Files need to be refactored to be under 500 lines each")
        sys.exit(1)
    else:
        print("\nLine count check PASSED")


if __name__ == "__main__":
    main()
