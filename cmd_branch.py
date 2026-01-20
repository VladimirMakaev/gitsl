"""Handler for 'git branch' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git branch' command.

    Translations:
    - git branch              -> sl bookmark (list)
    - git branch <name>       -> sl bookmark <name> (create)
    - git branch -d <name>    -> sl bookmark -d <name> (delete)
    - git branch -D <name>    -> sl bookmark -d <name> (safe delete)

    SAFETY: git branch -D just removes the label. sl bookmark -D strips
    commits. We ALWAYS use -d to preserve commits.
    """
    args = list(parsed.args)

    # CRITICAL: Translate -D to -d to avoid destroying commits
    # git -D: force delete label, commits preserved
    # sl -D: delete label AND strip commits (destructive!)
    args = ['-d' if a == '-D' else a for a in args]

    return run_sl(["bookmark"] + args)
