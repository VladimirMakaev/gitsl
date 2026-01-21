"""Handler for 'git commit' command.

Supported flags:
- SAFE-01: -a/--all -> REMOVED (dangerous semantic difference)
- COMM-01: --amend -> sl amend command
- COMM-02: --no-edit -> omit -e with amend (default sl amend behavior)
- COMM-03: -F/--file -> -l (logfile)
- COMM-04: --author -> -u (user)
- COMM-05: --date -> -d (date)
- COMM-06: -v/--verbose -> warning (different semantics)
- COMM-07: -s/--signoff -> custom trailer implementation
- COMM-08: -n/--no-verify -> warning (not supported)
"""

import subprocess
import sys
import tempfile
import os
from common import ParsedCommand, run_sl


def get_user_identity() -> str:
    """Get user identity from sl config for signoff trailer."""
    result = subprocess.run(
        ['sl', 'config', 'ui.username'],
        capture_output=True, text=True
    )
    return result.stdout.strip() or "Unknown User <unknown@example.com>"


def add_signoff_trailer(message: str, identity: str) -> str:
    """Append Signed-off-by trailer to message if not already present."""
    trailer = f"Signed-off-by: {identity}"
    if trailer not in message:
        return message.rstrip() + "\n\n" + trailer
    return message


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git commit' command.

    Translates to 'sl commit' or 'sl amend' and passes through arguments.
    """
    args = list(parsed.args)
    sl_args = []
    remaining_args = []

    # Extract flags
    amend = False
    no_edit = False
    signoff = False
    verbose = False
    no_verify = False
    message = None
    message_file = None
    author = None
    date_value = None

    i = 0
    while i < len(args):
        arg = args[i]

        # SAFE-01: Skip -a/--all flags (dangerous semantic difference)
        if arg in ('-a', '--all'):
            i += 1
            continue

        # COMM-01: --amend
        if arg == '--amend':
            amend = True
            i += 1
            continue

        # COMM-02: --no-edit
        if arg == '--no-edit':
            no_edit = True
            i += 1
            continue

        # COMM-06: -v/--verbose
        if arg in ('-v', '--verbose'):
            verbose = True
            i += 1
            continue

        # COMM-07: -s/--signoff
        if arg in ('-s', '--signoff'):
            signoff = True
            i += 1
            continue

        # COMM-08: -n/--no-verify
        if arg in ('-n', '--no-verify'):
            no_verify = True
            i += 1
            continue

        # -m/--message handling (need to capture for signoff)
        if arg == '-m':
            if i + 1 < len(args):
                message = args[i + 1]
                i += 2
                continue
        elif arg.startswith('-m'):
            # -m"message" format (attached)
            message = arg[2:]
            i += 1
            continue
        elif arg == '--message':
            if i + 1 < len(args):
                message = args[i + 1]
                i += 2
                continue
        elif arg.startswith('--message='):
            message = arg.split('=', 1)[1]
            i += 1
            continue

        # COMM-03: -F/--file
        if arg in ('-F', '--file'):
            if i + 1 < len(args):
                message_file = args[i + 1]
                i += 2
                continue
        elif arg.startswith('-F'):
            # -F<file> format (attached)
            message_file = arg[2:]
            i += 1
            continue
        elif arg.startswith('--file='):
            message_file = arg.split('=', 1)[1]
            i += 1
            continue

        # COMM-04: --author
        if arg == '--author':
            if i + 1 < len(args):
                author = args[i + 1]
                i += 2
                continue
        elif arg.startswith('--author='):
            author = arg.split('=', 1)[1]
            i += 1
            continue

        # COMM-05: --date
        if arg == '--date':
            if i + 1 < len(args):
                date_value = args[i + 1]
                i += 2
                continue
        elif arg.startswith('--date='):
            date_value = arg.split('=', 1)[1]
            i += 1
            continue

        # Pass through other args
        remaining_args.append(arg)
        i += 1

    # Print warnings for unsupported flags
    if verbose:
        print("Note: -v/--verbose in git shows diff in editor. "
              "Sapling -v shows repository info. Proceeding without -v.",
              file=sys.stderr)

    if no_verify:
        print("Warning: --no-verify not directly supported. "
              "Sapling has no native hook bypass. "
              "Pre-commit hooks will still run.",
              file=sys.stderr)

    # Build sl command
    if amend:
        sl_args.append('amend')
        # sl amend reuses message by default (like git --no-edit)
        # Add -e to match git's default (open editor) unless:
        # - --no-edit is present, OR
        # - a message is provided via -m or -F (no editor needed)
        if not no_edit and not message and not message_file:
            sl_args.append('-e')
    else:
        sl_args.append('commit')

    # Handle signoff
    temp_file = None
    if signoff:
        identity = get_user_identity()
        if message:
            # Add signoff to message
            message = add_signoff_trailer(message, identity)
        elif message_file:
            # Read file, add signoff, write to temp file
            try:
                with open(message_file, 'r') as f:
                    file_content = f.read()
                new_content = add_signoff_trailer(file_content, identity)
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                temp_file.write(new_content)
                temp_file.close()
                message_file = temp_file.name
            except Exception as e:
                print(f"Error reading message file: {e}", file=sys.stderr)
                return 1
        else:
            # No -m or -F, add signoff trailer via temp file for interactive editor
            identity = get_user_identity()
            trailer = f"\n\nSigned-off-by: {identity}"
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            temp_file.write(trailer)
            temp_file.close()
            # For interactive mode, we append the trailer via a template approach
            # Use -l with a temp file that just has the trailer, then -e to edit
            message_file = temp_file.name
            # Force editor mode so user can add their message above the trailer
            if amend and '-e' not in sl_args:
                sl_args.append('-e')

    # Add message or file
    if message:
        sl_args.extend(['-m', message])
    elif message_file:
        sl_args.extend(['-l', message_file])

    # COMM-04: --author -> -u
    if author:
        sl_args.extend(['-u', author])

    # COMM-05: --date -> -d
    if date_value:
        sl_args.extend(['-d', date_value])

    sl_args.extend(remaining_args)

    try:
        return run_sl(sl_args)
    finally:
        # Cleanup temp file if created
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
