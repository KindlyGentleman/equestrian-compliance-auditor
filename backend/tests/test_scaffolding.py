"""Automated verification test for TICK-0101: Project Scaffolding & Environment."""
from pathlib import Path


def test_directory_structure():
    """Verify that all core project directories and module markers exist."""
    base_dir = Path(__file__).resolve().parent.parent.parent

    expected_dirs = [
        base_dir / "backend" / "app" / "api",
        base_dir / "backend" / "app" / "core",
        base_dir / "backend" / "app" / "ingestion",
        base_dir / "backend" / "app" / "models",
        base_dir / "backend" / "app" / "rag",
        base_dir / "backend" / "app" / "engine",
        base_dir / "backend" / "app" / "data" / "regulations" / "fei",
        base_dir / "backend" / "app" / "data" / "regulations" / "brand",
        base_dir / "backend" / "tests",
        base_dir / "frontend",
        base_dir / "tickets",
    ]

    for directory in expected_dirs:
        assert directory.exists(), f"Missing required directory: {directory}"
        assert directory.is_dir(), f"Expected a directory, found file: {directory}"

    expected_init_files = [
        base_dir / "backend" / "app" / "__init__.py",
        base_dir / "backend" / "app" / "api" / "__init__.py",
        base_dir / "backend" / "app" / "core" / "__init__.py",
        base_dir / "backend" / "app" / "ingestion" / "__init__.py",
        base_dir / "backend" / "app" / "models" / "__init__.py",
        base_dir / "backend" / "app" / "rag" / "__init__.py",
        base_dir / "backend" / "app" / "engine" / "__init__.py",
        base_dir / "backend" / "tests" / "__init__.py",
    ]

    for init_file in expected_init_files:
        assert init_file.exists(), f"Missing module marker: {init_file}"


def test_gitignore_rules():
    """Verify that critical files and secret patterns are in .gitignore."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    gitignore_path = base_dir / ".gitignore"
    assert gitignore_path.exists(), ".gitignore file must exist"

    content = gitignore_path.read_text(encoding="utf-8")
    critical_patterns = [
        ".venv",
        ".env",
        "__pycache__",
        "qdrant_storage",
    ]
    for pattern in critical_patterns:
        assert pattern in content, f".gitignore missing pattern: {pattern}"


def test_git_repo_initialized():
    """Verify that git repository has been initialized."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    git_dir = base_dir / ".git"
    assert git_dir.exists(), ".git repository directory must exist"
    assert git_dir.is_dir(), ".git must be a directory"


if __name__ == "__main__":
    test_directory_structure()
    test_gitignore_rules()
    test_git_repo_initialized()
    print("ALL TICK-0101 TESTS PASSED SUCCESSFULLY!")
