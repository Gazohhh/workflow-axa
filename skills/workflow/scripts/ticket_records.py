"""Read existing checkbox tickets and labelled ticket blocks without migrating either.

This is a record parser, not proof that checks passed. Explicit incomplete evidence is
reported conservatively; conflicting historical prose needs reconciliation by the owner.
A TODO overview table (columns Ticket and Status, optionally Dependencies) is a summary,
never a state source: `overview` reports every row that disagrees with the tickets.
"""
from __future__ import annotations

import re
from typing import NamedTuple

ID = r'[A-Za-z][\w-]*(?:\.[\w-]+)*(?:/[A-Za-z][\w-]*(?:\.[\w-]+)*)?'
BOX = re.compile(r'^\s*[-*]\s+\[(?P<mark>[ xX~!-])\]\s*(?P<text>.+)$')  # rc3 L1: `- [ ]D3/T3` is still a ticket
TITLE_ID = re.compile(r'^(' + ID + r')(?![\w-]|\.\w)')
HEADING = re.compile(r'^(#{2,6})\s+(' + ID + r')\s+[—–-]\s+(.+)$')
REVISION = re.compile(r'\b(?:revision|card items|card follow-up)\s+([A-Za-z]\d[\w.-]*)\b', re.I)
FIELD = re.compile(r'^\s*(?:[-*]\s+)?(?:\*\*)?(Status|Verification|Owner acceptance|Blockers?|Evidence|Decision)(?:\*\*)?:\s*(.*?)\s*$', re.I)
EVIDENCE = re.compile(r'\bV(?:\d|[-_])[\w.-]*\b|\b(?:proof|evidence|verified)\s*:\s*\S|\bFINDINGS\b', re.I)
INCOMPLETE = re.compile(r'\b(?:not (?:yet )?(?:run|verified|accepted)|unverified|untested|pending|blocked|unavailable|limited|failed|unknown|tbd|needs (?:a )?human)\b', re.I)
CLOSED = re.compile(r'\b(?:cancelled|canceled|superseded|removed|not applicable|waived|(?:dropped|skipped) by (?:the )?owner)\b', re.I)
NONE = {'', '-', 'none', 'no', 'not applicable', 'n/a', 'not blocked'}
# Ticket sections (TASK-FOLDER.md). "How to verify" holds planned checks; results go on Verification/Owner acceptance.
SECTION = re.compile(r'^\s*(?:[-*]\s+)?(?:\*\*)?(What needs to happen|What should work|Technical details|How to verify|'
                     r'References)(?:\*\*)?:', re.I)
HUMAN = re.compile(r'\b(?:human check|needs (?:a )?human)\b', re.I)
DEPENDS = re.compile(r'^\s*(?:[-*]\s+)?(?:\*\*)?Depends on(?:\*\*)?:\s*(.*)$', re.I)
TICKET_REF = re.compile(r'(?<![\w/])(?:[A-Za-z]+\d[\w.]*/)?T\d[\w.]*(?![\w/])')
# The ticket states TASK-FOLDER.md lists, plus legacy done/complete. Anything else is reported, not guessed
# (rc3 trial L1: a tidy wrote "Status: box checked" and a verified ticket read as open).
STATES = re.compile(r'^(?:not started|ready|in progress|implemented|review|verified|blocked|paused|cancell?ed|'
                    r'superseded|removed|not applicable|done|complete|waived|(?:dropped|skipped) by (?:the )?owner)\b', re.I)


class Ticket(NamedTuple):
    start: int
    end: int
    identifier: str
    qualified: str
    text: str
    mark: str | None
    fields: dict[str, list[tuple[int, str]]]
    incomplete: bool

    def value(self, name: str) -> str:
        return '; '.join(value for _, value in self.fields.get(name, []))

    @property
    def state(self) -> str:
        return self.value('status').casefold()

    @property
    def blocked(self) -> bool:
        return (bool(re.search(r'\bblocked\b', self.state))
                or any(value.casefold() not in NONE for _, value in self.fields.get('blocker', []))
                or (self.mark is not None and bool(re.search(r'\bblocked\b', self.text, re.I))))

    @property
    def unclear(self) -> str:
        """Why the Status cannot be read as a ticket state: several different values, or an unlisted one."""
        values = list(dict.fromkeys(value.strip().casefold() for _, value in self.fields.get('status', [])))
        if len(values) > 1:
            return 'conflicting Status lines: ' + ' / '.join(values)
        if values and not STATES.match(values[0]):
            return f'Status "{values[0]}" is not a listed ticket state'
        return ''

    @property
    def closed(self) -> bool:
        return self.mark == '-' or bool(CLOSED.search(self.state if self.state else self.text))

    @property
    def complete_claim(self) -> bool:
        return self.mark in ('x', 'X') or bool(re.match(r'^(?:verified|done|complete)(?:\b|$)', self.state))

    @property
    def has_evidence(self) -> bool:
        return (bool(EVIDENCE.search(self.text))
                or any(value.casefold() not in NONE and not INCOMPLETE.search(value)
                       for _, value in self.fields.get('evidence', [])))

    @property
    def category(self) -> str:
        if self.unclear:  # first: "stopped (build cancelled ...)" is not a cancelled ticket (P2 live test)
            return 'unclear'
        if self.closed:
            return 'closed'
        if self.complete_claim:
            return 'unbacked' if self.incomplete or self.blocked or not self.has_evidence else 'done'
        if self.blocked:
            return 'blocked'
        if 'paused' in self.state:
            return 'paused'
        if self.mark in ('~', '!') or re.match(r'^(?:in progress|implemented|review)', self.state):
            return 'in_progress'
        return 'open'

    @property
    def display(self) -> str:
        text = self.text
        if self.mark is None:
            return (self.qualified + ' — ' + text)[:140]
        if self.qualified != self.identifier:
            text = self.qualified + text[len(self.identifier):]
        return text[:140]


def parse(lines: list[str]) -> list[Ticket]:
    """Headings name tickets; revision sections qualify old repeated IDs. Fences are ignored."""
    starts, headings = [], []
    revision = ''
    fence = None
    block_level = None
    visible = set()
    for number, line in enumerate(lines):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            char = marker[1][0]
            fence = None if fence == char else char if fence is None else fence
            continue
        if fence:
            continue
        visible.add(number)
        heading = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading:
            if block_level is not None and len(heading[1]) <= block_level:
                block_level = None
            headings.append((number, len(heading[1])))
            context = REVISION.search(heading[2])
            if context:
                revision = context[1]
            elif len(heading[1]) <= 2:
                revision = ''
        block = HEADING.match(line)
        box = BOX.match(line)
        if block:
            identifier, text, mark, level = block[2], block[3], None, len(block[1])
            block_level = level
        elif box:
            if block_level is not None:
                continue  # acceptance checkboxes belong to their labelled ticket
            found = TITLE_ID.match(box['text'])
            identifier = found[1] if found else ''
            text, mark, level = box['text'], box['mark'], 7
        else:
            continue
        qualified = (revision + '/' + identifier) if revision and identifier and '/' not in identifier else identifier
        starts.append((number, identifier, qualified, text, mark, level))
    tickets = []
    for index, (start, identifier, qualified, text, mark, level) in enumerate(starts):
        end = starts[index+1][0] if index+1 < len(starts) else len(lines)
        end = next((n for n, depth in headings if start < n < end and depth <= level), end)
        fields: dict[str, list[tuple[int, str]]] = {}
        for n in range(start+1, end):
            match = FIELD.match(lines[n]) if n in visible else None
            if match:
                key = match[1].casefold().replace('blockers', 'blocker')
                fields.setdefault(key, []).append((n, match[2]))
        explicit = ' '.join(value for key in ('status', 'verification', 'owner acceptance', 'evidence')
                            for _, value in fields.get(key, []))
        incomplete = bool(INCOMPLETE.search(explicit + (' ' + text if mark is not None else '')))
        if any(len(fields.get(key, [])) > 1 for key in ('status', 'verification', 'owner acceptance')):
            incomplete = True
        if mark is None and any(n in visible and re.match(r'^\s*[-*]\s+\[ \]', lines[n]) for n in range(start+1, end)):
            incomplete = True
        if mark is None and HUMAN.search(' '.join(section_text(lines, visible, start, end, 'how to verify'))):
            if not any(v.casefold() not in NONE for _, v in fields.get('owner acceptance', [])):
                incomplete = True  # a required human check with no recorded result is outstanding verification
        tickets.append(Ticket(start, end, identifier, qualified, text, mark, fields, incomplete))
    return tickets


def select(tickets: list[Ticket], identifier: str) -> list[Ticket]:
    """An unqualified repeated ID stays ambiguous even when only one of its uses is open."""
    return [ticket for ticket in tickets if (ticket.qualified == identifier if '/' in identifier
                                             else ticket.identifier == identifier)]


def section_text(lines: list[str], visible: set[int], start: int, end: int, name: str) -> list[str]:
    """One ticket section's text: from its label to the next section label or field line."""
    out, inside = [], False
    for n in range(start + 1, end):
        if n not in visible:
            continue
        label = SECTION.match(lines[n])
        if label or FIELD.match(lines[n]):
            inside = bool(label) and label[1].casefold() == name
            if inside:
                out.append(lines[n][label.end():])
            continue
        if inside:
            out.append(lines[n])
    return out


class Problem(NamedTuple):
    line: int        # 0-based line the problem points at
    tickets: tuple   # qualified IDs it concerns (empty when the row names no ticket)
    message: str


class Row(NamedTuple):
    line: int
    cells: list      # (start, end) character span of each cell
    status: int      # index of the Status cell
    ticket: 'Ticket | None'


def _cells(line: str) -> list[tuple[int, int]]:
    pipes = [m.start() for m in re.finditer(r'(?<!\\)\|', line)]
    spans = list(zip(pipes, pipes[1:]))
    if pipes and line[pipes[-1] + 1:].strip():
        spans.append((pipes[-1], len(line)))
    return [(a + 1, b) for a, b in spans]


def _plain(text: str) -> str:
    return re.sub(r'[*`]', '', text).strip()


def _state(value: str) -> str:
    found = STATES.match(' '.join(value.casefold().split()))
    return found[0].replace('canceled', 'cancelled') if found else ''


def overview(lines: list[str], parsed: list[Ticket] | None = None) -> tuple[list[Row], list[Problem]]:
    """Rows of every overview table (a `|` table whose header has Ticket and Status cells) and their problems.

    The tickets are the source: a row never sets or decides a state. Reported: a row whose ticket is missing,
    ambiguous, repeated or a checkbox ticket; a Status or Dependencies cell that differs from the ticket's Status
    or Depends on line; and, once a table exists, a ticket without a row."""
    parsed = parse(lines) if parsed is None else parsed
    rows, problems, fence, n = [], [], None, 0
    while n < len(lines):
        line = lines[n]
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            char = marker[1][0]
            fence = None if fence == char else char if fence is None else fence
        if (fence or marker or not line.lstrip().startswith('|') or n + 1 >= len(lines)
                or not re.match(r'^\s*\|?\s*:?-{3,}', lines[n + 1])):
            n += 1
            continue
        header = [_plain(line[a:b]).casefold() for a, b in _cells(line)]
        n += 2
        if 'ticket' not in header or 'status' not in header:
            continue
        col, status = header.index('ticket'), header.index('status')
        depends = header.index('dependencies') if 'dependencies' in header else None
        while n < len(lines) and lines[n].lstrip().startswith('|'):
            spans = _cells(lines[n])
            cell = [_plain(lines[n][a:b]) for a, b in spans]
            name = cell[col] if len(cell) > max(col, status) else ''
            matches = select(parsed, name) if re.fullmatch(ID, name) else []
            ticket = matches[0] if len(matches) == 1 else None
            rows.append(Row(n, spans, status, ticket))
            where = f'overview row {name or "(empty)"} at line {n + 1}'
            if len(matches) > 1:
                names = tuple(t.qualified for t in matches)
                problems.append(Problem(n, names, f'{where} is ambiguous ({", ".join(names)}); use the qualified ID'))
            elif not ticket:
                problems.append(Problem(n, (), f'{where} names no ticket in this file'))
            elif ticket.mark is not None:
                problems.append(Problem(n, (ticket.qualified,), f'{where} summarises a checkbox ticket; the table '
                                        'can only summarise tickets with a Status line'))
            else:
                if ticket.unclear:
                    problems.append(Problem(n, (ticket.qualified,), f'{where} cannot be checked: the ticket\'s '
                                            f'status is unreadable ({ticket.unclear})'))
                elif not _state(cell[status]) or _state(cell[status]) != _state(ticket.state):
                    problems.append(Problem(n, (ticket.qualified,), f'{where} says Status "{cell[status]}" but '
                                            f'the ticket says "{ticket.value("status") or "(none)"}"'))
                deps = [m[1] for m in (DEPENDS.match(lines[k]) for k in range(ticket.start + 1, ticket.end)) if m]
                if depends is not None and len(cell) > depends and deps and \
                        set(TICKET_REF.findall(cell[depends])) != set(TICKET_REF.findall(' '.join(deps))):
                    problems.append(Problem(n, (ticket.qualified,), f'{where} lists dependencies '
                                            f'"{cell[depends]}" but the ticket says "{"; ".join(deps)}"'))
            n += 1
    if rows:
        counted: dict[str, int] = {}
        for row in rows:
            if row.ticket:
                counted[row.ticket.qualified] = counted.get(row.ticket.qualified, 0) + 1
        for ticket in parsed:
            if counted.get(ticket.qualified, 0) > 1:
                problems.append(Problem(ticket.start, (ticket.qualified,),
                                        f'{ticket.qualified} has {counted[ticket.qualified]} overview rows'))
            elif not counted.get(ticket.qualified) and not any(ticket.qualified in p.tickets for p in problems):
                problems.append(Problem(ticket.start, (ticket.qualified,),
                                        f'{ticket.qualified} (line {ticket.start + 1}) has no overview row'))
    return rows, problems
