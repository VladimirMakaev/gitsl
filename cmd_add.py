"""Handler for 'git add' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git add' command.

    Translations:
    - git add <files>  -> sl add <files>
    - git add -A       -> sl addremove
    - git add --all    -> sl addremove
    """
    # Check for -A or --all flag -> translate to addremove
    if "-A" in parsed.args or "--all" in parsed.args:
        # Filter out the -A/--all flag
        filtered_args = [a for a in parsed.args if a not in ("-A", "--all")]
        return run_sl(["addremove"] + filtered_args)

    # Standard add passthrough
    return run_sl(["add"] + parsed.args)
