"""Diagnose only (T20): at session start, name second copies of workflow-axa skills and explain the ways to resolve
them. It never blocks, deletes, changes or writes anything. The note also warns when the imported shared rules
differ from the plugin's, and names an enabled plugin whose process skills overlap the workflow-axa phases.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys

# An import line in the global CLAUDE.md, for example @C:/Users/me/.agents/skills/rule-maker/rules/START.md
IMPORT = re.compile(r'^[ \t]*@(.*[\\/]rule-maker[\\/]rules)[\\/]START\.md[ \t]*\r?$', re.MULTILINE)


def plugin_root() -> Path:
    return Path(os.environ.get('CLAUDE_PLUGIN_ROOT') or Path(__file__).resolve().parents[1])


def config_dir() -> Path | None:
    """The Claude Code profile folder, or None when no home folder is known."""
    try:
        return Path(os.environ.get('CLAUDE_CONFIG_DIR') or Path.home() / '.claude')
    except RuntimeError:
        return None


def project_root(cwd: object) -> Path | None:
    """The nearest folder upward from the start folder that holds .git, else the start folder. None without one."""
    if not isinstance(cwd, str) or not cwd:
        return None
    start = Path(cwd)
    try:
        return next((folder for folder in (start, *start.parents) if (folder / '.git').exists()), start)
    except (OSError, ValueError):
        return start


def project_places(cwd: object) -> list[Path]:
    """Project skills folders Claude Code loads: the start folder and each parent up to the repository root."""
    top = project_root(cwd)
    if top is None:
        return []
    start = Path(cwd)
    return [folder / '.claude' / 'skills' for folder in (start, *start.parents) if folder == top or top in folder.parents]


def skill_names(root: Path) -> list[str]:
    """Folder names the plugin registers; plugin.json is the only name list."""
    try:
        skills = json.loads((root / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8-sig'))['skills']
    except (OSError, ValueError, KeyError, TypeError):
        return []
    if not isinstance(skills, list):
        return []
    names = [item.replace('\\', '/').rstrip('/').rsplit('/', 1)[-1] for item in skills if isinstance(item, str)]
    return [name for name in names if name]


def find_duplicates(root: Path, places: list[Path]) -> list[str]:
    """Full paths of entries in the given skills folders that hold a SKILL.md for a registered name."""
    found = []
    seen = set()
    names = skill_names(root)
    for place in places:
        try:
            key = os.path.normcase(os.path.abspath(place))
        except (OSError, ValueError):
            continue
        if key in seen:
            continue  # a session started in the home folder names the personal folder twice
        seen.add(key)
        for name in names:
            entry = place / name
            try:
                present = (entry / 'SKILL.md').is_file()
            except (OSError, ValueError):
                present = False
            if present:
                found.append(str(entry))
    return found


# Skills that start workflow change work; they wait while a second copy exists.
LINK_NOTE = 'If an entry is a link, remove only the link, not the folder it points at. '


def found_copies(paths: list[str]) -> str:
    """The path list and the risk, shared by the session start message and the deny reason."""
    return ('workflow-axa found a second copy of one or more of its skills in these places:\n'
            + '\n'.join(paths)
            + '\nA second copy of a workflow-axa skill can give different results from the copy in the plugin. ')


def duplicate_message(paths: list[str]) -> str:
    return (found_copies(paths)
            + 'Tell the user this in your first reply, show the paths above and explain the ways to settle it, so '
              'they can choose. One: delete or rename the extra entries. Two: keep both and always call the skills '
              'with the workflow-axa: prefix, because a bare name may load either copy. Three: turn off the source '
              'they do not want. ' + LINK_NOTE + 'Do not change them yourself. Nothing is paused.')


def differing_rules_copy(root: Path, config: Path) -> Path | None:
    """The rules folder the global CLAUDE.md imports, when a plugin rules file is missing or different there."""
    try:
        text = (config / 'CLAUDE.md').read_text(encoding='utf-8-sig', errors='replace')
        found = IMPORT.search(text)
        if not found:
            return None
        copy = config / Path(found.group(1)).expanduser()
        own = root / 'skills' / 'rule-maker' / 'rules'
        if copy.resolve() == own.resolve():
            return None
        for source in sorted(own.iterdir()):
            if not source.is_file():
                continue
            other = copy / source.name
            if not other.is_file() or other.read_bytes() != source.read_bytes():
                return copy
    except (OSError, ValueError, RuntimeError):
        return None
    return None


def rules_message(copy: Path) -> str:
    return (f'The shared rules folder {copy} differs from the rules in the workflow-axa plugin. '
            'Tell the user to reinstall or update that copy. This does not pause work.')


# Other plugins whose process skills overlap the workflow-axa phases: (plugin name, ((the workflow-axa skill to use,
# the plugin's skills it replaces), ...)). The note is added to every session while such a plugin is on, so it stays
# short.
OVERLAPPING_PLUGINS = (
    ('superpowers', (('workflow-clarify', ('brainstorming',)),
                     ('workflow-specify', ('writing-plans',)),
                     ('workflow-execute', ('executing-plans', 'subagent-driven-development')),
                     ('tdd', ('test-driven-development',)),
                     ('code-review', ('requesting-code-review',)),
                     ('workflow-deliver', ('verification-before-completion',)))),
)


def plugin_switches(path: Path) -> dict:
    """The enabledPlugins object of one settings file, or an empty one when the file is missing or malformed."""
    try:
        plugins = json.loads(path.read_text(encoding='utf-8-sig')).get('enabledPlugins')
    except (OSError, ValueError, AttributeError, RecursionError):
        return {}
    return plugins if isinstance(plugins, dict) else {}


def enabled_plugins(config: Path, cwd: object) -> set[str]:
    """Names, without the marketplace part, of the plugins the Claude settings enable. For each plugin the most
    specific file that switches it decides: project local, then project, then user."""
    files = [config / 'settings.json']
    top = project_root(cwd)
    if top is not None:
        files += [top / '.claude' / 'settings.json', top / '.claude' / 'settings.local.json']
    switches: dict[str, bool] = {}
    for path in files:  # least specific first, so a later file overrides
        for key, value in plugin_switches(path).items():
            if isinstance(key, str) and isinstance(value, bool):
                switches[key] = value
    return {key.split('@', 1)[0] for key, value in switches.items() if value}


def overlap_message(plugin: str, overlaps: tuple) -> str:
    uses = [f'{ours} instead of {" and ".join(theirs)}' for ours, theirs in overlaps]
    listed = uses[0] if len(uses) == 1 else ' and '.join(uses) if len(uses) == 2 else \
        f'{", ".join(uses[:-1])}, and {uses[-1]}'
    # Settings files say what is enabled, not what this session loaded (a session can exclude user settings).
    return (f'Your settings enable the {plugin} plugin. If loaded here, its skills overlap the workflow-axa '
            'phases. '
            f'While a workflow-axa task runs, use {listed}. '
            f'Do not change plugin settings yourself. The user can disable {plugin} for this project.')


def session_start(root: Path, config: Path, duplicates: list[str], event: dict) -> None:
    notes = []
    if duplicates:
        notes.append(duplicate_message(duplicates))
    copy = differing_rules_copy(root, config)
    if copy:
        notes.append(rules_message(copy))
    enabled = enabled_plugins(config, event.get('cwd'))
    notes.extend(overlap_message(plugin, overlaps) for plugin, overlaps in OVERLAPPING_PLUGINS if plugin in enabled)
    if notes:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart',
                                                 'additionalContext': '\n'.join(notes)}}))


def current_duplicates(event: dict) -> list[str]:
    """Looked up again on every event, so a deleted copy stops counting without a restart."""
    config = config_dir()
    if config is None:
        return []
    return find_duplicates(plugin_root(), [config / 'skills', *project_places(event.get('cwd'))])


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (ValueError, RecursionError):
        return 0
    if not isinstance(event, dict):
        return 0
    kind = event.get('hook_event_name')
    if kind == 'SessionStart':
        config = config_dir()
        if config is not None:
            session_start(plugin_root(), config, current_duplicates(event), event)
    return 0


if __name__ == '__main__':
    sys.exit(main())
