"""Handler for 'git grep' command.

Supported flags:
- GREP-01: -n/--line-number -> -n (show line numbers)
- GREP-02: -i/--ignore-case -> -i (case insensitive)
- GREP-03: -l/--files-with-matches -> -l (files only)
- GREP-04: -c/--count -> warning (not supported)
- GREP-05: -w/--word-regexp -> -w (word match)
- GREP-06: -v/--invert-match -> -V (CRITICAL: sl uses uppercase V)
- GREP-07: -A <num> -> -A <num> (lines after)
- GREP-08: -B <num> -> -B <num> (lines before)
- GREP-09: -C <num> -> -C <num> (context lines)
- GREP-10: -h -> warning (shows help in sl, not suppress filename)
- GREP-11: -H -> no-op (already default behavior)
- GREP-12: -o/--only-matching -> warning (not supported)
- GREP-13: -q/--quiet -> warning (not supported, use grep | wc -l to check)
- GREP-14: -F/--fixed-strings -> -F (literal strings)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git grep' command.

    Translations:
    - git grep <pattern>     -> sl grep <pattern>
    - git grep -n <pattern>  -> sl grep -n <pattern>
    - git grep -i <pattern>  -> sl grep -i <pattern>
    - git grep -l <pattern>  -> sl grep -l <pattern>
    - git grep -v <pattern>  -> sl grep -V <pattern> (uppercase V!)
    - git grep -A5 <pattern> -> sl grep -A 5 <pattern>
    - git grep -B5 <pattern> -> sl grep -B 5 <pattern>
    - git grep -C5 <pattern> -> sl grep -C 5 <pattern>
    - git grep -w <pattern>  -> sl grep -w <pattern>
    - git grep -F <pattern>  -> sl grep -F <pattern>

    Unsupported (with warnings):
    - git grep -c  -> warning: use sl grep | wc -l
    - git grep -h  -> warning: cannot suppress filenames
    - git grep -o  -> warning: use sl grep | grep -o
    - git grep -q  -> warning: use sl grep | wc -l (no quiet mode)
    - git grep -H  -> no-op (already default)

    All other arguments pass through unchanged.
    """
    sl_args = ["grep"]
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # GREP-01: -n/--line-number passes through
        if arg in ('-n', '--line-number'):
            sl_args.append('-n')

        # GREP-02: -i/--ignore-case passes through
        elif arg in ('-i', '--ignore-case'):
            sl_args.append('-i')

        # GREP-03: -l/--files-with-matches passes through
        elif arg in ('-l', '--files-with-matches'):
            sl_args.append('-l')

        # GREP-04: -c/--count - not supported, warn
        elif arg in ('-c', '--count'):
            print("Warning: -c/--count not supported by Sapling grep. "
                  "Consider: sl grep <pattern> | wc -l",
                  file=sys.stderr)

        # GREP-05: -w/--word-regexp passes through
        elif arg in ('-w', '--word-regexp'):
            sl_args.append('-w')

        # GREP-06: -v/--invert-match -> -V (CRITICAL: sl uses uppercase V)
        elif arg in ('-v', '--invert-match'):
            sl_args.append('-V')

        # GREP-07: -A <num> - lines after match
        elif arg == '-A':
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-A', parsed.args[i]])
        elif arg.startswith('-A') and len(arg) > 2:
            # Attached format: -A5
            sl_args.extend(['-A', arg[2:]])

        # GREP-08: -B <num> - lines before match
        elif arg == '-B':
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-B', parsed.args[i]])
        elif arg.startswith('-B') and len(arg) > 2:
            # Attached format: -B5
            sl_args.extend(['-B', arg[2:]])

        # GREP-09: -C <num> - context lines (before and after)
        elif arg == '-C':
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-C', parsed.args[i]])
        elif arg.startswith('-C') and len(arg) > 2:
            # Attached format: -C5
            sl_args.extend(['-C', arg[2:]])

        # GREP-10: -h - suppress filename (sl -h shows help instead!)
        elif arg == '-h':
            print("Warning: -h (suppress filename) not supported by Sapling grep. "
                  "Filenames will be shown.",
                  file=sys.stderr)
            # Do NOT pass through - would show help instead

        # GREP-11: -H - force filename (already default behavior, no-op)
        elif arg == '-H':
            # Silently skip - sl grep already shows filenames by default
            pass

        # GREP-12: -o/--only-matching - not supported, warn
        elif arg in ('-o', '--only-matching'):
            print("Warning: -o/--only-matching not supported by Sapling grep. "
                  "Consider: sl grep <pattern> | grep -o <pattern>",
                  file=sys.stderr)

        # GREP-13: -q/--quiet - not supported by sl grep, warn
        elif arg in ('-q', '--quiet'):
            print("Warning: -q/--quiet not supported by Sapling grep. "
                  "Use exit code from: sl grep <pattern> | wc -l",
                  file=sys.stderr)

        # GREP-14: -F/--fixed-strings passes through
        elif arg in ('-F', '--fixed-strings'):
            sl_args.append('-F')

        # Everything else passes through unchanged
        else:
            remaining_args.append(arg)

        i += 1

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
