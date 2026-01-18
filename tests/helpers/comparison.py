"""
Output comparison utilities for E2E testing.
"""

import difflib
import re
from typing import List

from .commands import CommandResult


def normalize_for_semantic(text: str) -> List[str]:
    """
    Normalize text for semantic comparison.

    - Strips leading/trailing whitespace per line
    - Collapses multiple whitespace to single space
    - Removes empty lines

    Returns:
        List of normalized non-empty lines
    """
    lines = []
    for line in text.splitlines():
        line = line.strip()
        line = re.sub(r"\s+", " ", line)
        if line:
            lines.append(line)
    return lines


def compare_exact(expected: str, actual: str) -> bool:
    """Exact string comparison."""
    return expected == actual


def compare_semantic(expected: str, actual: str) -> bool:
    """
    Semantic comparison ignoring whitespace differences.

    Ignores:
    - Leading/trailing whitespace per line
    - Multiple consecutive spaces
    - Empty lines
    """
    return normalize_for_semantic(expected) == normalize_for_semantic(actual)


def generate_diff(expected: str, actual: str, context_lines: int = 3) -> str:
    """
    Generate unified diff for error messages.

    Args:
        expected: Expected output
        actual: Actual output
        context_lines: Lines of context around differences

    Returns:
        Unified diff string
    """
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile="expected",
        tofile="actual",
        n=context_lines,
    )
    return "".join(diff)


def assert_output_match(
    expected: str,
    actual: str,
    mode: str = "exact",
    message: str = "Output mismatch",
) -> None:
    """
    Assert outputs match according to mode.

    Args:
        expected: Expected output
        actual: Actual output
        mode: "exact" or "semantic"
        message: Custom message prefix

    Raises:
        AssertionError with diff on mismatch
    """
    compare_fn = compare_exact if mode == "exact" else compare_semantic

    if not compare_fn(expected, actual):
        diff = generate_diff(expected, actual)
        raise AssertionError(f"{message} ({mode} mode):\n{diff}")


def assert_commands_equal(
    git_result: CommandResult,
    gitsl_result: CommandResult,
    mode: str = "exact",
) -> None:
    """
    Assert git and gitsl produced equivalent results.

    Always compares exit codes exactly.
    Compares stdout using specified mode.

    Args:
        git_result: Result from running git command
        gitsl_result: Result from running gitsl command
        mode: "exact" or "semantic" for stdout comparison

    Raises:
        AssertionError with details on mismatch
    """
    # Exit codes must match exactly
    assert git_result.exit_code == gitsl_result.exit_code, (
        f"Exit code mismatch: "
        f"git={git_result.exit_code}, gitsl={gitsl_result.exit_code}\n"
        f"git stderr: {git_result.stderr}\n"
        f"gitsl stderr: {gitsl_result.stderr}"
    )

    # Compare stdout using specified mode
    assert_output_match(
        git_result.stdout,
        gitsl_result.stdout,
        mode=mode,
        message="stdout mismatch",
    )
