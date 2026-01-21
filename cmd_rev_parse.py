"""Handler for 'git rev-parse' command."""

import os.path
import subprocess
import sys
from common import ParsedCommand


def _handle_show_toplevel() -> int:
    """REVP-01: --show-toplevel returns repository root path."""
    result = subprocess.run(
        ["sl", "root"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        sys.stderr.write(result.stderr)
    return result.returncode


def _handle_git_dir() -> int:
    """REVP-02: --git-dir returns .sl or .hg directory path."""
    result = subprocess.run(
        ["sl", "root"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        root = result.stdout.strip()
        # Check for .sl first (newer Sapling), then .hg
        sl_dir = os.path.join(root, ".sl")
        hg_dir = os.path.join(root, ".hg")
        if os.path.isdir(sl_dir):
            print(sl_dir)
        elif os.path.isdir(hg_dir):
            print(hg_dir)
        else:
            # Fallback to .sl (expected location)
            print(sl_dir)
        return 0
    else:
        sys.stderr.write(result.stderr)
    return result.returncode


def _handle_is_inside_work_tree() -> int:
    """REVP-03: --is-inside-work-tree returns true/false."""
    result = subprocess.run(
        ["sl", "root"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("true")
    else:
        print("false")
    # Note: git always returns 0 for this flag, even outside repo
    return 0


def _handle_abbrev_ref(ref: str) -> int:
    """REVP-04: --abbrev-ref HEAD returns current bookmark name."""
    if ref.upper() == "HEAD":
        result = subprocess.run(
            ["sl", "log", "-r", ".", "-T", "{activebookmark}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            bookmark = result.stdout.strip()
            if bookmark:
                print(bookmark)
            else:
                # No active bookmark - equivalent to detached HEAD
                print("HEAD")
            return 0
        else:
            sys.stderr.write(result.stderr)
            return result.returncode
    else:
        # For other refs, just echo back the ref name
        print(ref)
        return 0


def _handle_verify(ref: str) -> int:
    """REVP-05: --verify validates object reference exists."""
    result = subprocess.run(
        ["sl", "log", "-r", ref, "-T", "{node}", "-l", "1"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        node = result.stdout.strip()
        if node:
            print(node)
            return 0
    # Match git's error message format
    sys.stderr.write("fatal: Needed a single revision\n")
    return 128  # Match git's exit code


def _handle_symbolic(ref: str) -> int:
    """REVP-06: --symbolic outputs ref in symbolic form."""
    # Symbolic means output the input form (e.g., HEAD stays HEAD)
    print(ref)
    return 0


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rev-parse' command.

    Supports:
    - --short HEAD: returns short commit hash (7 chars)
    - --show-toplevel: returns repository root path
    - --git-dir: returns .sl directory path
    - --is-inside-work-tree: returns true/false
    - --abbrev-ref HEAD: returns current bookmark name
    - --verify <ref>: validates object reference
    - --symbolic <ref>: outputs in symbolic form
    """
    args = parsed.args

    # REVP-01: --show-toplevel
    if "--show-toplevel" in args:
        return _handle_show_toplevel()

    # REVP-02: --git-dir
    if "--git-dir" in args:
        return _handle_git_dir()

    # REVP-03: --is-inside-work-tree
    if "--is-inside-work-tree" in args:
        return _handle_is_inside_work_tree()

    # REVP-04: --abbrev-ref
    if "--abbrev-ref" in args:
        idx = args.index("--abbrev-ref")
        ref = args[idx + 1] if idx + 1 < len(args) else "HEAD"
        return _handle_abbrev_ref(ref)

    # REVP-05: --verify
    if "--verify" in args:
        idx = args.index("--verify")
        if idx + 1 < len(args):
            return _handle_verify(args[idx + 1])
        else:
            sys.stderr.write("fatal: --verify requires a revision\n")
            return 128

    # REVP-06: --symbolic
    if "--symbolic" in args:
        idx = args.index("--symbolic")
        ref = args[idx + 1] if idx + 1 < len(args) else "HEAD"
        return _handle_symbolic(ref)

    # Existing: --short HEAD pattern (either order)
    if "--short" in args and "HEAD" in args:
        result = subprocess.run(
            ["sl", "whereami"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # sl whereami returns 40 chars, git rev-parse --short returns 7
            short_hash = result.stdout.strip()[:7]
            print(short_hash)
        else:
            sys.stderr.write(result.stderr)
        return result.returncode

    # Unsupported rev-parse variants
    sys.stderr.write("gitsl: rev-parse flag not supported. Supported: --show-toplevel, --git-dir, --is-inside-work-tree, --abbrev-ref HEAD, --verify, --symbolic, --short HEAD\n")
    return 1
