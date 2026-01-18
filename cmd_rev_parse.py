"""Handler for 'git rev-parse' command."""

import subprocess
import sys
from common import ParsedCommand


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rev-parse' command.

    Currently only supports: --short HEAD -> sl whereami (truncated to 7 chars)
    """
    # Check for --short HEAD pattern (either order)
    if "--short" in parsed.args and "HEAD" in parsed.args:
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
            # Pass through error
            sys.stderr.write(result.stderr)
        return result.returncode

    # Unsupported rev-parse variants
    sys.stderr.write("gitsl: rev-parse currently only supports --short HEAD\n")
    return 1
