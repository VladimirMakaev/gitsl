"""Handler for 'git log' command.

Supported flags:
- LOG-01: --graph -> -G (commit graph)
- LOG-02: --stat -> --stat (diffstat)
- LOG-03: --patch/-p -> -p (show diffs)
- LOG-04: --author=<pattern> -> -u <pattern> (filter by author)
- LOG-05: --grep=<pattern> -> -k <pattern> (filter by commit message)
- LOG-06: --no-merges -> --no-merges (exclude merge commits)
- LOG-07: --all -> --all (all commits)
- LOG-08: --follow -> -f (follow file renames)
- LOG-09: --since/--after -> -d ">date" (commits after date)
- LOG-10: --until/--before -> -d "<date" (commits before date)
- LOG-11: --name-only -> template with files
- LOG-12: --name-status -> template with file status
- LOG-13: --decorate -> template with bookmarks
- LOG-14: --pretty/--format -> -T template
- LOG-15: --first-parent -> revset approximation
- LOG-16: --reverse -> revset with reverse()
- LOG-17: -S<string> -> warning (pickaxe not supported)
- LOG-18: -G<regex> -> warning (pickaxe not supported)
- LOG-19: -n/--max-count -> -l (already implemented)
- LOG-20: --oneline -> template (already implemented)
"""

import re
import sys
from common import ParsedCommand, run_sl


# Template for --oneline format
# Uses sl's {node|short} (12 chars) - semantic match per ROADMAP
ONELINE_TEMPLATE = "{node|short} {desc|firstline}\\n"

# Template for --name-only format
NAME_ONLY_TEMPLATE = "{node|short} {desc|firstline}\\n{files}\\n"

# Template for --name-status format (shows add/delete/modify status)
NAME_STATUS_TEMPLATE = ("{node|short} {desc|firstline}\\n"
                        "{file_adds % 'A\\t{file}\\n'}"
                        "{file_dels % 'D\\t{file}\\n'}"
                        "{file_copies % 'C\\t{file}\\n'}\\n")

# Template for --decorate (shows bookmarks on commits)
DECORATE_TEMPLATE = "{node|short} ({bookmarks}) {desc|firstline}\\n"

# Preset formats for --pretty
PRETTY_PRESETS = {
    'oneline': "{node|short} {desc|firstline}\\n",
    'short': "commit {node|short}\\nAuthor: {author}\\n\\n    {desc|firstline}\\n\\n",
    'medium': "commit {node|short}\\nAuthor: {author}\\nDate:   {date|isodate}\\n\\n    {desc|firstline}\\n\\n",
    'full': "commit {node}\\nAuthor: {author}\\nCommit: {author}\\n\\n    {desc}\\n\\n",
}

# Git format placeholders to sl template keywords
GIT_TO_SL_PLACEHOLDERS = {
    '%H': '{node}',
    '%h': '{node|short}',
    '%s': '{desc|firstline}',
    '%b': '{desc}',
    '%an': '{author|person}',
    '%ae': '{author|email}',
    '%ad': '{date|isodate}',
    '%ar': '{date|age}',
    '%d': '{bookmarks}',
    '%n': '\\n',
}


def translate_format_placeholders(git_format: str) -> str:
    """Translate git format placeholders to sl template keywords."""
    result = git_format
    for git_placeholder, sl_keyword in GIT_TO_SL_PLACEHOLDERS.items():
        result = result.replace(git_placeholder, sl_keyword)
    # Ensure newline at end
    if not result.endswith('\\n'):
        result += '\\n'
    return result


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git log' command.

    Translations:
    - git log --oneline -> sl log -T '<template>'
    - git log -N -> sl log -l N
    - git log -n N -> sl log -l N
    - git log -nN -> sl log -l N
    - git log --max-count=N -> sl log -l N
    - git log --graph -> sl log -G
    - git log --stat -> sl log --stat
    - git log --patch/-p -> sl log -p
    - git log --author=<pattern> -> sl log -u <pattern>
    - git log --grep=<pattern> -> sl log -k <pattern>
    - git log --no-merges -> sl log --no-merges
    - git log --all -> sl log --all
    - git log --follow -> sl log -f
    - git log --since/--after -> sl log -d ">date"
    - git log --until/--before -> sl log -d "<date"

    All other arguments pass through unchanged.
    """
    sl_args = ["log"]
    remaining_args = []
    use_oneline = False
    limit = None
    since_date = None
    until_date = None
    name_only = False
    name_status = False
    decorate = False
    custom_template = None
    use_reverse = False
    use_first_parent = False

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # --oneline flag
        if arg == "--oneline":
            use_oneline = True

        # -N format (e.g., -5, -10)
        elif re.match(r'^-(\d+)$', arg):
            limit = arg[1:]

        # -n N format (space between)
        elif arg == "-n":
            if i + 1 < len(parsed.args):
                limit = parsed.args[i + 1]
                i += 1

        # -nN format (attached number)
        elif arg.startswith("-n") and len(arg) > 2 and arg[2:].isdigit():
            limit = arg[2:]

        # --max-count=N format
        elif arg.startswith("--max-count="):
            limit = arg.split("=", 1)[1]

        # LOG-01: --graph -> -G
        elif arg == '--graph':
            sl_args.append('-G')

        # LOG-02: --stat passes through
        elif arg == '--stat':
            sl_args.append('--stat')

        # LOG-03: --patch/-p passes through
        elif arg in ('--patch', '-p'):
            sl_args.append('-p')

        # LOG-04: --author=<pattern> -> -u <pattern>
        elif arg.startswith('--author='):
            pattern = arg.split('=', 1)[1]
            sl_args.extend(['-u', pattern])
        elif arg == '--author':
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-u', parsed.args[i]])

        # LOG-05: --grep=<pattern> -> -k <pattern>
        elif arg.startswith('--grep='):
            pattern = arg.split('=', 1)[1]
            sl_args.extend(['-k', pattern])
        elif arg == '--grep':
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-k', parsed.args[i]])

        # LOG-06: --no-merges passes through
        elif arg == '--no-merges':
            sl_args.append('--no-merges')

        # LOG-07: --all passes through
        elif arg == '--all':
            sl_args.append('--all')

        # LOG-08: --follow -> -f
        elif arg == '--follow':
            sl_args.append('-f')

        # LOG-09: --since/--after -> -d ">date"
        elif arg.startswith('--since=') or arg.startswith('--after='):
            since_date = arg.split('=', 1)[1]
        elif arg in ('--since', '--after'):
            if i + 1 < len(parsed.args):
                i += 1
                since_date = parsed.args[i]

        # LOG-10: --until/--before -> -d "<date"
        elif arg.startswith('--until=') or arg.startswith('--before='):
            until_date = arg.split('=', 1)[1]
        elif arg in ('--until', '--before'):
            if i + 1 < len(parsed.args):
                i += 1
                until_date = parsed.args[i]

        # LOG-11: --name-only -> template with file names
        elif arg == '--name-only':
            name_only = True

        # LOG-12: --name-status -> template with file status
        elif arg == '--name-status':
            name_status = True

        # LOG-13: --decorate -> template with bookmarks
        elif arg == '--decorate':
            decorate = True

        # LOG-14: --pretty/--format -> -T template
        elif arg.startswith('--pretty=') or arg.startswith('--format='):
            format_spec = arg.split('=', 1)[1]
            # Handle preset names
            if format_spec in PRETTY_PRESETS:
                custom_template = PRETTY_PRESETS[format_spec]
            # Handle format:... custom format
            elif format_spec.startswith('format:'):
                custom_template = translate_format_placeholders(format_spec[7:])
            # Handle raw format string (no format: prefix)
            else:
                custom_template = translate_format_placeholders(format_spec)
        elif arg in ('--pretty', '--format'):
            if i + 1 < len(parsed.args):
                i += 1
                format_spec = parsed.args[i]
                if format_spec in PRETTY_PRESETS:
                    custom_template = PRETTY_PRESETS[format_spec]
                elif format_spec.startswith('format:'):
                    custom_template = translate_format_placeholders(format_spec[7:])
                else:
                    custom_template = translate_format_placeholders(format_spec)

        # LOG-15: --first-parent -> use revset approximation
        elif arg == '--first-parent':
            use_first_parent = True

        # LOG-16: --reverse -> use revset with reverse()
        elif arg == '--reverse':
            use_reverse = True

        # LOG-17: -S<string> (pickaxe) -> warning, not supported
        elif arg.startswith('-S'):
            search_term = arg[2:] if len(arg) > 2 else ''
            if len(arg) == 2 and i + 1 < len(parsed.args):
                i += 1
                search_term = parsed.args[i]
            print("Warning: -S pickaxe search not supported in Sapling.", file=sys.stderr)
            print(f"Consider: sl log -p | grep '{search_term}'", file=sys.stderr)

        # LOG-18: -G<regex> (regex pickaxe) -> warning, not supported
        # Note: Must check after -G for graph since --graph is already handled
        elif arg.startswith('-G') and len(arg) > 2:
            search_pattern = arg[2:]
            print("Warning: -G regex pickaxe search not supported in Sapling.", file=sys.stderr)
            print(f"Consider: sl log -p | grep -E '{search_pattern}'", file=sys.stderr)

        # Everything else passes through
        else:
            remaining_args.append(arg)

        i += 1

    # Build sl command - determine template to use
    # Priority: custom_template > name_status > name_only > decorate > oneline
    template = None
    if custom_template:
        template = custom_template
    elif name_status:
        template = NAME_STATUS_TEMPLATE
    elif name_only:
        template = NAME_ONLY_TEMPLATE
    elif decorate:
        template = DECORATE_TEMPLATE
    elif use_oneline:
        template = ONELINE_TEMPLATE

    if template:
        sl_args.extend(["-T", template])

    if limit is not None:
        sl_args.extend(["-l", limit])

    # Build date filter for sl -d
    if since_date and until_date:
        sl_args.extend(['-d', f'{since_date} to {until_date}'])
    elif since_date:
        sl_args.extend(['-d', f'>{since_date}'])
    elif until_date:
        sl_args.extend(['-d', f'<{until_date}'])

    # Build revset for --reverse and --first-parent
    # These use sl's revset language to approximate git behavior
    if use_reverse or use_first_parent:
        revset_parts = []
        if use_first_parent:
            # Approximate --first-parent by following only first parent in ancestry
            # This is a simplification; exact git behavior is more complex
            revset_parts.append("first(ancestors(.))")
        if use_reverse:
            # Wrap in reverse() to show oldest first
            if revset_parts:
                revset_parts = [f"reverse({revset_parts[0]})"]
            else:
                revset_parts.append("reverse(ancestors(.))")
        sl_args.extend(['-r', revset_parts[0]])

    sl_args.extend(remaining_args)

    return run_sl(sl_args)
