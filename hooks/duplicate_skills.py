"""Name second copies of workflow-axa skills at session start and ask the owner to delete them.

While a copy exists, Skill calls that start workflow change work are refused, until the copies are gone or the
user says "continue with duplicates" in that session. The script never deletes or changes a skill, never stops a
session from starting, and writes one thing only: an empty override marker per session in the gate cache folder.
The session start note also names an enabled plugin whose process skills overlap the workflow-axa phases. That
note only informs: it pauses nothing and changes no setting.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time

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
CHANGE_SKILLS = ('workflow-clarify', 'workflow-specify', 'workflow-execute')
PAUSED = ', '.join(CHANGE_SKILLS[:-1]) + ' and ' + CHANGE_SKILLS[-1]  # the messages name what the check pauses
# The whole message must be the words, so "do not continue with duplicates" never lifts the pause.
OVERRIDE = re.compile(r'[\s"\'“”‘’`]*continue\s+with\s+duplicates[\s"\'“”‘’`.!]*', re.IGNORECASE)
WORDS = re.compile(r'continue\s+with\s+duplicates', re.IGNORECASE)
# Context the host or the editor adds around typed text. Agent messages, notifications and command output are
# never the exact words, so they need no list of their own.
HOST_CONTEXT = re.compile(r'<(system-reminder|ide_\w+)>')
# A change skill typed as a slash command loads without a Skill tool call.
TYPED = re.compile(r'(?:^\s*|<command-name>\s*)/(?:workflow-axa:)?(workflow-(?:clarify|specify|execute))(?![\w/.-])')
OVERRIDE_SECONDS = 12 * 3600  # a resumed session keeps its ID, so the override must end by itself
MARKER = 'duplicates-ok-'
LINK_NOTE = 'If an entry is a link, remove only the link, not the folder it points at. '


def found_copies(paths: list[str]) -> str:
    """The path list and the risk, shared by the session start message and the deny reason."""
    return ('workflow-axa found a second copy of one or more of its skills in these places:\n'
            + '\n'.join(paths)
            + '\nA second copy of a workflow-axa skill can give different results from the copy in the plugin. ')


def duplicate_message(paths: list[str], lifted: bool) -> str:
    if lifted:
        state = f'The pause is lifted for this session. The skills {PAUSED} load until that ends.'
    else:
        state = (f'The skills {PAUSED} stay paused until the entries are gone '
                 'or the user sends a message that is only the words "continue with duplicates".')
    return (found_copies(paths)
            + 'Tell the user this in your first reply, show the paths above and ask the user to delete the listed '
              'entries. ' + LINK_NOTE + 'Do not delete them yourself. ' + state)


def deny_reason(paths: list[str]) -> str:
    return (found_copies(paths)
            + f'The skills {PAUSED} wait until this is settled. There are two ways out. '
              'One: show the paths above and ask the user to delete the listed entries. ' + LINK_NOTE
            + 'Two: the user sends a message that is only the words "continue with duplicates", which lifts the '
              'pause for this session. '
              'Do not delete them yourself. Do not say these words for the user.')


def block_reason(paths: list[str]) -> str:
    """Shown to the user when a typed change command is stopped."""
    return (found_copies(paths)
            + 'This command waits until that is settled. Delete the listed entries and send the command again. '
            + LINK_NOTE
            + 'Or send a message that is only the words "continue with duplicates" to work with both copies '
              'in this session.')


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
    return (f'The {plugin} plugin is also enabled. Its process skills overlap the workflow-axa phases. '
            f'While a workflow-axa task runs, use {listed}. '
            f'Do not change plugin settings yourself. The user can disable {plugin} for this project.')


def session_start(root: Path, config: Path, duplicates: list[str], event: dict) -> None:
    notes = []
    if duplicates:
        notes.append(duplicate_message(duplicates, pause_lifted(event.get('session_id'))))
    copy = differing_rules_copy(root, config)
    if copy:
        notes.append(rules_message(copy))
    enabled = enabled_plugins(config, event.get('cwd'))
    notes.extend(overlap_message(plugin, overlaps) for plugin, overlaps in OVERLAPPING_PLUGINS if plugin in enabled)
    if notes:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart',
                                                 'additionalContext': '\n'.join(notes)}}))


def override_marker(session: object) -> Path | None:
    """The empty file that records "continue with duplicates" for one session, or None without a session ID."""
    if not isinstance(session, str) or not session:
        return None
    folder = Path(os.environ.get('WORKFLOW_AXA_GATE_CACHE') or Path(tempfile.gettempdir()) / 'workflow-axa-gate')
    return folder / (MARKER + hashlib.sha256(session.encode('utf-8', 'replace')).hexdigest()[:32])


def can_hold_a_marker(folder: Path) -> bool:
    """False when the cache path, or the nearest existing folder above it, is not a folder."""
    for part in (folder, *folder.parents):
        if part.exists():
            return part.is_dir()
    return False


def pause_lifted(session: object) -> bool:
    """True when the user lifted the pause for this session, or when no override could ever be stored or read:
    a guard defect must not block work."""
    try:
        marker = override_marker(session)
        if marker is None:
            return False
        if not can_hold_a_marker(marker.parent):
            return True
        state = marker.stat()
    except FileNotFoundError:
        return False
    except (OSError, ValueError):
        return True
    return stat.S_ISREG(state.st_mode) and 0 <= time.time() - state.st_mtime < OVERRIDE_SECONDS


def store_override(session: object) -> None:
    """Write the marker, the only file this script writes, and remove this script's own expired markers."""
    try:
        marker = override_marker(session)
        if marker is None:
            return
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
        for other in marker.parent.glob(MARKER + '*'):
            own = re.fullmatch(re.escape(MARKER) + '[0-9a-f]{32}', other.name)
            if own and other.is_file() and time.time() - other.stat().st_mtime >= OVERRIDE_SECONDS:
                other.unlink()
    except (OSError, ValueError):
        pass  # nothing stored; pause_lifted decides whether work can go on


def typed_text(prompt: str) -> str:
    """The prompt without closed system-reminder and IDE blocks. One pass, so a long prompt stays fast."""
    kept, position, unclosed = [], 0, set()
    for opening in HOST_CONTEXT.finditer(prompt):
        if opening.start() < position or opening.group(1) in unclosed:
            continue
        closing = f'</{opening.group(1)}>'
        end = prompt.find(closing, opening.end())
        if end < 0:
            unclosed.add(opening.group(1))
            continue
        kept.append(prompt[position:opening.start()])
        position = end + len(closing)
    kept.append(prompt[position:])
    return ' '.join(kept)


def user_prompt(event: dict) -> None:
    """Store the override when the whole message is the words; stop a typed change command while a copy exists."""
    prompt = event.get('prompt')
    if not isinstance(prompt, str):
        return
    # Cheap test first: removing host context from a long prompt is slow.
    if WORDS.search(prompt) and OVERRIDE.fullmatch(typed_text(prompt)):
        store_override(event.get('session_id'))
        return
    if not TYPED.search(prompt):
        return
    duplicates = current_duplicates(event)
    if duplicates and not pause_lifted(event.get('session_id')):
        print(json.dumps({'decision': 'block', 'reason': block_reason(duplicates)}))


def skill_call(event: dict) -> None:
    """Refuse a Skill call while a second copy exists and the user has not lifted the pause for this session."""
    tool_input = event.get('tool_input')
    skill = tool_input.get('skill') if isinstance(tool_input, dict) else None
    if event.get('tool_name') != 'Skill' or not isinstance(skill, str):
        return
    skill = skill.strip().lstrip('/').casefold()
    duplicates = current_duplicates(event)
    # A bare name can resolve to the second copy; a prefixed name always names one plugin's copy.
    bare_duplicate = ':' not in skill and skill in (Path(entry).name.casefold() for entry in duplicates)
    if not duplicates or (skill.rsplit(':', 1)[-1] not in CHANGE_SKILLS and not bare_duplicate):
        return
    if pause_lifted(event.get('session_id')):
        return
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                             'permissionDecisionReason': deny_reason(duplicates)}}))


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
    if kind == 'UserPromptSubmit':
        user_prompt(event)
    elif kind == 'PreToolUse':
        skill_call(event)
    elif kind == 'SessionStart':
        config = config_dir()
        if config is not None:
            session_start(plugin_root(), config, current_duplicates(event), event)
    return 0


if __name__ == '__main__':
    sys.exit(main())
