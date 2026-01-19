"""Handler for 'git switch' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git switch' command.

    Translations:
    - git switch <branch>      -> sl goto <bookmark>
    - git switch -c <name>     -> sl bookmark <name>
    """
    args = list(parsed.args)

    # Check for create flag
    if '-c' in args or '--create' in args:
        # Extract branch name after -c
        for i, arg in enumerate(args):
            if arg in ('-c', '--create') and i + 1 < len(args):
                branch_name = args[i + 1]
                return run_sl(["bookmark", branch_name])

    # Standard switch -> goto
    return run_sl(["goto"] + args)
