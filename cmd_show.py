"""Handler for 'git show' command.

Supported flags:
- SHOW-01: --stat -> --stat (diffstat summary)
- SHOW-02: -U<n> -> -U <n> (context lines)
- SHOW-03: -w/--ignore-all-space -> -w (ignore whitespace)
- SHOW-04: --name-only -> template with file names
- SHOW-05: --name-status -> template with file status
- SHOW-06: --pretty/--format -> -T template
- SHOW-07: -s/--no-patch -> template (suppress diff)
- SHOW-08: --oneline -> template (short format)
"""

import sys
from common import ParsedCommand, run_sl


# Template for --oneline format
# Uses sl's {node|short} (12 chars) - semantic match per ROADMAP
SHOW_ONELINE_TEMPLATE = "{node|short} {desc|firstline}\\n"

# Template for --name-only format
SHOW_NAME_ONLY_TEMPLATE = "{node|short} {desc|firstline}\\n{files}\\n"

# Template for --name-status format (shows add/delete/modify status)
SHOW_NAME_STATUS_TEMPLATE = ("{node|short} {desc|firstline}\\n"
                              "{file_adds % 'A\\t{file}\\n'}"
                              "{file_dels % 'D\\t{file}\\n'}"
                              "{file_mods % 'M\\t{file}\\n'}\\n")

# Template for -s/--no-patch (commit info only, no diff)
SHOW_NO_PATCH_TEMPLATE = ("commit {node|short}\\n"
                          "Author: {author}\\n"
                          "Date:   {date|isodate}\\n\\n"
                          "    {desc}\\n")

# Preset formats for --pretty (copied from cmd_log.py pattern)
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
    Handle 'git show' command.

    Translations:
    - git show          -> sl show (current commit)
    - git show <commit> -> sl show <commit>
    - git show --stat   -> sl show --stat
    - git show -U<n>    -> sl show -U <n>
    - git show -w       -> sl show -w
    - git show --name-only -> sl show -T template
    - git show --name-status -> sl show -T template
    - git show --pretty=<format> -> sl show -T template
    - git show -s/--no-patch -> sl show -T template
    - git show --oneline -> sl show -T template

    Template priority: custom_template > name_status > name_only > no_patch > oneline

    All other arguments pass through unchanged.
    """
    sl_args = ["show"]
    remaining_args = []
    use_oneline = False
    no_patch = False
    name_only = False
    name_status = False
    custom_template = None

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # SHOW-01: --stat passes through
        if arg == '--stat':
            sl_args.append('--stat')

        # SHOW-02: -U<n> with value parsing
        elif arg.startswith('-U') and len(arg) > 2 and arg[2:].isdigit():
            # Attached value: -U5
            sl_args.extend(['-U', arg[2:]])
        elif arg == '-U':
            # Separate value: -U 5
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-U', parsed.args[i]])

        # SHOW-03: -w/--ignore-all-space passes through
        elif arg in ('-w', '--ignore-all-space'):
            sl_args.append('-w')

        # SHOW-04: --name-only
        elif arg == '--name-only':
            name_only = True

        # SHOW-05: --name-status
        elif arg == '--name-status':
            name_status = True

        # SHOW-06: --pretty/--format
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

        # SHOW-07: -s/--no-patch (suppress diff output)
        elif arg in ('-s', '--no-patch'):
            no_patch = True

        # SHOW-08: --oneline
        elif arg == '--oneline':
            use_oneline = True

        # Everything else passes through
        else:
            remaining_args.append(arg)

        i += 1

    # Build sl command - determine template to use
    # Priority: custom_template > name_status > name_only > no_patch > oneline
    template = None
    if custom_template:
        template = custom_template
    elif name_status:
        template = SHOW_NAME_STATUS_TEMPLATE
    elif name_only:
        template = SHOW_NAME_ONLY_TEMPLATE
    elif no_patch:
        template = SHOW_NO_PATCH_TEMPLATE
    elif use_oneline:
        template = SHOW_ONELINE_TEMPLATE

    if template:
        sl_args.extend(["-T", template])

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
