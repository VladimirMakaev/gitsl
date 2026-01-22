"""Handler for 'git blame' command.

Supported flags:
- BLAM-01: -w -> -w/--ignore-all-space (ignore whitespace)
- BLAM-02: -b -> --ignore-space-change (CRITICAL: sl -b has different meaning!)
- BLAM-03: -L <start>,<end> -> warning (line range not supported)
- BLAM-04: -e/--show-email -> warning (not supported)
- BLAM-05: -p/--porcelain -> warning (not supported)
- BLAM-06: -l -> warning (CRITICAL: sl -l means line number, not long hash!)
- BLAM-07: -n/--show-number -> -n (show line numbers)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git blame' command.

    Translations:
    - git blame <file>    -> sl annotate <file>
    - git blame -w <file> -> sl annotate -w <file>
    - git blame -b <file> -> sl annotate --ignore-space-change <file>
    - git blame -n <file> -> sl annotate -n <file>

    Unsupported (with warnings):
    - git blame -L <range> -> warning: use sl annotate | sed
    - git blame -e         -> warning: email not available
    - git blame -p         -> warning: porcelain not supported
    - git blame -l         -> warning: long hash not supported

    Note: sl has 'blame' as an alias for 'annotate'.
    """
    sl_args = ["annotate"]
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # BLAM-01: -w -> -w (ignore all whitespace)
        if arg in ('-w', '--ignore-all-space'):
            sl_args.append('-w')

        # BLAM-02: -b -> --ignore-space-change
        # CRITICAL: git -b means "ignore space changes"
        # sl -b means "blank SHA1 for boundary commits" - completely different!
        elif arg == '-b':
            sl_args.append('--ignore-space-change')

        # BLAM-03: -L <start>,<end> - line range (not supported)
        elif arg == '-L':
            if i + 1 < len(parsed.args):
                i += 1
                line_range = parsed.args[i]
            else:
                line_range = "?"
            print(f"Warning: -L {line_range} line range not supported by Sapling annotate. "
                  f"Consider: sl annotate <file> | sed -n '{line_range}p'",
                  file=sys.stderr)
        elif arg.startswith('-L') and len(arg) > 2:
            # Attached format: -L10,20
            line_range = arg[2:]
            print(f"Warning: -L{line_range} line range not supported by Sapling annotate. "
                  f"Consider: sl annotate <file> | sed -n '{line_range}p'",
                  file=sys.stderr)

        # BLAM-04: -e/--show-email - not supported
        elif arg in ('-e', '--show-email'):
            print("Warning: -e/--show-email not supported by Sapling annotate. "
                  "Author names are shown by default.",
                  file=sys.stderr)

        # BLAM-05: -p/--porcelain - not supported
        elif arg in ('-p', '--porcelain'):
            print("Warning: -p/--porcelain output not supported by Sapling annotate. "
                  "Use -T template for custom output format.",
                  file=sys.stderr)

        # BLAM-06: -l - long hash (NOT SUPPORTED)
        # CRITICAL: sl -l means "show line number at first appearance" - different!
        elif arg == '-l':
            print("Warning: -l (long revision hash) not supported by Sapling annotate. "
                  "Sapling shows short hashes by default.",
                  file=sys.stderr)
            # Do NOT pass through - sl -l has completely different meaning

        # BLAM-07: -n/--show-number -> -n (show line numbers)
        elif arg in ('-n', '--show-number'):
            sl_args.append('-n')

        # Everything else passes through unchanged
        else:
            remaining_args.append(arg)

        i += 1

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
