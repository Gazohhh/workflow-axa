"""Regression cases from the reported rc.2 trial and the owner's ticket example.

These are helper/contract tests, not live-agent behavior or spending enforcement.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import test_phase_gate_hook as fixtures


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def record(*args):
    return subprocess.run([sys.executable, '-X', 'utf8', '-I', str(ROOT/'skills/workflow/scripts/record.py'),
                           *map(str, args)], capture_output=True, text=True, encoding='utf-8')


class PackageLocationTests(unittest.TestCase):
    def setUp(self):
        self.hook = load(ROOT/'hooks/truncated_read.py', 'rc3_partial')

    def test_git_bash_target_matches_actual_root_not_its_basename(self):
        found = self.hook.partial_reads('cd /c/cache/vendor/release-17/skills && cat workflow/TASK-FOLDER.md | head -2',
                                       'C:/cache/vendor/release-17')
        self.assertTrue(found)

    def test_quoted_paths_and_parent_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'plugin cache'/'release 17'
            folder = root/'skills/workflow'
            folder.mkdir(parents=True)
            (folder/'RULES.md').write_text('rule\n'*12, encoding='utf-8')
            self.assertTrue(self.hook.partial_reads(f'cd "{folder}" && cat RULES.md | head -2', str(root)))
            self.assertEqual(self.hook.partial_reads(f'cd "{folder}" && cat RULES.md | head -20', str(root)), [])
            self.assertEqual(self.hook.partial_reads(f'cd "{folder}" && cat ../../../outside.md | head -2', str(root)), [])

    def test_other_installation_not_claimed_by_a_matching_folder_name(self):
        self.assertFalse(self.hook.in_package('C:/other/workflow-axa/skills/workflow/SKILL.md',
                                             'C:/cache/vendor/release-17'))


class LegacyApprovalTests(unittest.TestCase):
    def setUp(self):
        self.h = fixtures.ApprovalGateTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)

    def test_named_legacy_report_with_actual_full_answer_keeps_authority(self):
        self.h.task(fixtures.TASK, '- Approval: legacy approved; report reviews/legacy-review.html; "Yes to both".', report='legacy-review.html')
        rows = [fixtures.ROUTER, self.h.records(), fixtures.say(f'Plan: docs/plans/{fixtures.TASK}/reviews/legacy-review.html. Approve?'), fixtures.user('Yes to both')]
        self.assertIsNone(self.h.decision(rows, 'Edit', {'file_path': self.h.code}))

    def test_legacy_without_user_answer_does_not_become_authorised(self):
        self.h.task(fixtures.TASK, '- Approval: legacy approved; report reviews/legacy-review.html; "Yes to both".', report='legacy-review.html')
        rows = [fixtures.ROUTER, self.h.records(), fixtures.say(f'Plan: docs/plans/{fixtures.TASK}/reviews/legacy-review.html. Approve?')]
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_legacy_cannot_cover_a_new_checkpoint_revision(self):
        self.h.task(fixtures.TASK, '- Approval: legacy approved; report reviews/legacy-review.html; "Yes to both".\n- Proposed revision: r2', report='legacy-review.html')
        rows = [fixtures.ROUTER, self.h.records(), fixtures.say(f'Plan: docs/plans/{fixtures.TASK}/reviews/legacy-review.html. Approve?'), fixtures.user('Yes to both')]
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_no_revision_block_offers_reconciliation_not_bypass(self):
        self.h.task(fixtures.TASK, '- Approval: approved; "Yes to both" (report reviews/legacy-review.html).', report='legacy-review.html')
        rows = [fixtures.ROUTER, self.h.records(), fixtures.say(f'Plan: docs/plans/{fixtures.TASK}/reviews/legacy-review.html. Approve?'), fixtures.user('Yes to both')]
        result = self.h.fire(rows, 'Edit', {'file_path': self.h.code})
        reason = result['permissionDecisionReason']
        self.assertIn('resume-task', reason)
        self.assertIn('Do not edit or disable the hook', reason)


class TicketFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.task = Path(self.tmp.name)
        self.todo = self.task/'TODO.md'
        self.items = load(ROOT/'skills/workflow/scripts/open_items.py', 'rc3_items')

    def write(self, content):
        self.todo.write_bytes(content.replace('\n', '\r\n').encode('utf-8'))


class ReadableTicketTests(TicketFixture):
    def test_readable_blocks_are_listed_and_evidence_is_not_lost(self):
        self.write('# TODO\n\n## Current work\n\n### D4/T8 — Keep the supported setting\nStatus: ready\n'
                   'Depends on: D4/T3\nVerification: not run\n\n### D4/T3 — Check both phones\n'
                   'Status: implemented — verification pending\nVerification: limited; second phone unavailable\n'
                   'Evidence: FINDINGS V3\n\n### R1/T1 — Completed check\nStatus: verified\n'
                   'Verification: passed\nEvidence: FINDINGS V1\n')
        row = self.items.scan(self.task)
        self.assertTrue(any('D4/T8' in s for s in row['open']))
        self.assertTrue(any('D4/T3' in s for s in row['in_progress']))
        self.assertEqual(row['done'], 1)

    def test_a_checked_item_with_a_required_check_missing_is_not_verified(self):
        self.write('- [x] T3 — both phones; verified: FINDINGS V3; OnePlus proof not run (not connected)\n')
        row = self.items.scan(self.task)
        self.assertEqual(row['done'], 0)
        self.assertTrue(row['unbacked'])

    def test_removed_work_is_closed_not_a_pass(self):
        self.write('- [x] T4 — Removed by owner; DECISIONS Q5; FINDINGS V2\n')
        row = self.items.scan(self.task)
        self.assertEqual(row['done'], 0)
        self.assertTrue(row.get('closed'))

    def test_conflicting_status_and_verification_is_reported(self):
        self.write('### T1 — Device check\nStatus: verified\nVerification: blocked; device unavailable\nEvidence: FINDINGS V1\n')
        row = self.items.scan(self.task)
        self.assertEqual(row['done'], 0)
        self.assertTrue(row['unbacked'])

    def test_tick_readable_block_preserves_crlf_and_history(self):
        self.write('### D4/T8 — Apply the approved fallback\nStatus: implemented\nVerification: passed\n'
                   'Evidence: FINDINGS V8\n\n## History\n\n### D3/T8 — Older task\nStatus: superseded\nDecision: Q21\n')
        result = record('tick', self.todo, 'D4/T8', 'FINDINGS V9')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        raw = self.todo.read_bytes()
        self.assertIn(b'Status: verified\r\n', raw)
        self.assertIn(b'Evidence: FINDINGS V8; FINDINGS V9\r\n', raw)
        self.assertIn(b'Status: superseded\r\nDecision: Q21', raw)
        self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))

    def test_tick_refuses_unresolved_verification(self):
        self.write('### T1 — Both phones\nStatus: implemented\nVerification: blocked\nBlocker: second phone missing\n')
        before = self.todo.read_bytes()
        result = record('tick', self.todo, 'T1', 'V1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('verification', result.stdout.lower())
        self.assertEqual(self.todo.read_bytes(), before)

    def test_repeated_legacy_id_requires_a_revision(self):
        self.write('## Revision D4\n- [ ] T3 — New task\n\n## Revision D3\n- [ ] T3 — Old task\n')
        before = self.todo.read_bytes()
        self.assertNotEqual(record('tick', self.todo, 'T3', 'V1').returncode, 0)
        self.assertEqual(self.todo.read_bytes(), before)
        result = record('tick', self.todo, 'D4/T3', 'V1')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(b'- [x] T3', self.todo.read_bytes())
        self.assertIn(b'## Revision D3\r\n- [ ] T3', self.todo.read_bytes())


class AdditionalTicketTests(TicketFixture):
    def test_checkbox_acceptance_belongs_to_the_ticket(self):
        self.write('### T1 — Handle errors\nStatus: verified\nEvidence: FINDINGS V1\nAcceptance:\n- [ ] Device result checked\n')
        row = self.items.scan(self.task)
        self.assertEqual(row['done'], 0)
        self.assertEqual(len(row['unbacked']), 1)
        self.assertEqual(row['open'], [])

    def test_duplicate_status_is_not_a_verified_result(self):
        self.write('### T1 — Check\nStatus: verified\nStatus: in progress\nEvidence: FINDINGS V1\n')
        self.assertEqual(self.items.scan(self.task)['done'], 0)
        before = self.todo.read_bytes()
        self.assertNotEqual(record('tick', self.todo, 'T1', 'V2').returncode, 0)
        self.assertEqual(self.todo.read_bytes(), before)

    def test_example_fences_do_not_create_live_tickets(self):
        self.write('# TODO\n```markdown\n### T9 — Example\nStatus: ready\n- [ ] T10 — Example\n```\n### T1 — Real\nStatus: ready\n')
        row = self.items.scan(self.task)
        self.assertEqual(len(row['open']), 1)
        self.assertIn('T1 — Real', row['open'][0])

    def test_multiline_legacy_evidence_is_supported(self):
        self.write('- [x] T1 — Check\n  Verification: passed\n  Evidence: FINDINGS V1\n')
        self.assertEqual(self.items.scan(self.task)['done'], 1)

    def test_placeholder_evidence_is_not_counted(self):
        self.write('### T1 — Check\nStatus: verified\nEvidence: FINDINGS TBD\n')
        self.assertTrue(self.items.scan(self.task)['unbacked'])

    def test_paused_is_not_completed_and_closed_is_not_passed(self):
        self.write('### T1 — Wait\nStatus: paused\n\n### T2 — Removed requirement\nStatus: removed\nDecision: Q5\n')
        row = self.items.scan(self.task)
        self.assertEqual(row['done'], 0)
        self.assertEqual(len(row['paused']), 1)
        self.assertEqual(len(row['closed']), 1)

    def test_missing_evidence_field_is_added_only_to_selected_block(self):
        self.write('### T1 — Complete check\nStatus: implemented\nVerification: passed\n\n### T2 — Next check\nStatus: ready\n')
        result = record('tick', self.todo, 'T1', 'FINDINGS V1')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('Status: verified\nEvidence: FINDINGS V1', self.todo.read_text())
        self.assertIn('### T2 — Next check\nStatus: ready', self.todo.read_text())


class TicketEvidenceTests(TicketFixture):
    def test_relative_evidence_pointer_is_not_forced_into_another_document(self):
        self.write('### T1 — Check\nStatus: verified\nVerification: passed\nEvidence: results/check.json\n')
        self.assertEqual(self.items.scan(self.task)['done'], 1)

    def test_empty_evidence_field_is_not_counted(self):
        self.write('### T1 — Check\nStatus: verified\nVerification: passed\nEvidence: none\n')
        self.assertTrue(self.items.scan(self.task)['unbacked'])

    def test_tick_cannot_supply_a_placeholder_or_incomplete_result(self):
        self.write('### T1 — Check\nStatus: implemented\nVerification: passed\n')
        before = self.todo.read_bytes()
        for evidence in ('none', 'TBD', 'FINDINGS V1; phone not run'):
            with self.subTest(evidence=evidence):
                result = record('tick', self.todo, 'T1', evidence)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.todo.read_bytes(), before)


class PermissionPolicyTests(unittest.TestCase):
    """Instruction contracts only. These are not a model obedience or billing test."""
    def test_plain_exception_is_not_an_agent_recommendation(self):
        design = (ROOT/'skills/rule-maker/rules/DESIGN.md').read_text()
        skill = (ROOT/'skills/ui-design/SKILL.md').read_text()
        for term in ('Do not recommend', 'Yes to all recommendations', 'whole user answer', 'named element'):
            self.assertIn(term, design)
        self.assertNotIn('same-tag elements or plain-by-instruction', skill)

    def test_cap_and_total_categories_cannot_be_inferred(self):
        policy = (ROOT/'skills/workflow/VISUAL-REVIEW.md').read_text()
        prompt = (ROOT/'docs/archive/CLAUDE-TEST-PROMPT.txt').read_text()
        for term in ('$[AMOUNT]', 'orchestration', 'retro', 'subtotal', 'does not meter'):
            self.assertIn(term, policy)
        for term in ('NO default cap', 'No real spending/production', 'read-only'):
            self.assertIn(term, prompt)
        self.assertIn('worker', (ROOT/'docs/archive/RC3-CASES.md').read_text())

    def test_current_protocol_does_not_require_missing_baseline(self):
        prompt = (ROOT/'docs/archive/CLAUDE-TEST-PROMPT.txt').read_text()
        self.assertIn('do not search for it', prompt)
        self.assertIn('No automatic retry', prompt)
        self.assertIn('No fixes', prompt)
        self.assertIn('do not call', prompt.casefold())


L1 = ROOT / 'tests/fixtures/l1-todo-tidy'  # TODO.md before and after the rc3 trial's L1 tidy, saved unchanged
# A tidy that keeps every recorded state readable: boxes stay boxes unless a listed Status says the same thing.
L1_COMPLIANT = """# TODO
Layout only: wording, states and IDs are as recorded before 2026-11-04.

## Open work
- [ ] D4/T3 -- player uses shared formatter (supports A2)
- [ ] D3/T3 -- tidy README wording

## Ticked, verification outstanding
- [x] T2 -- player path shows Final; needs human: phone check of the player screen

## Done

### T1 — Web formatter uses shared format_score
Status: verified
Evidence: FINDINGS V1

## Removed
- ~~T0 -- old score widget~~ removed by owner 2026-10-19 ("drop the widget")
"""


class L1TidyTests(TicketFixture):
    """rc3 trial L1: a readability tidy wrote "Status: box checked", and the verified T1 then read as open."""

    def states(self, text):
        return {t.qualified: t.category for t in self.items.tickets.parse(text.splitlines())}

    def test_the_original_records_read_as_recorded(self):
        before = (L1 / 'before.md').read_text(encoding='utf-8')
        self.assertEqual(self.states(before), {'T1': 'done', 'T2': 'unbacked', 'D4/T3': 'open', 'D3/T3': 'open'})

    def test_unlisted_statuses_from_the_trial_tidy_are_reported_not_open_or_verified(self):
        self.write((L1 / 'trial-after.md').read_text(encoding='utf-8'))
        row = self.items.scan(self.task)
        self.assertEqual((row['done'], row['open'], row['unbacked']), (0, [], []))
        self.assertEqual(len(row['unclear']), 4)
        self.assertTrue(all('not a listed ticket state' in item for item in row['unclear']))
        before = self.todo.read_bytes()
        result = record('tick', self.todo, 'D4/T3', 'FINDINGS V2')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unreadable status', result.stdout)
        self.assertEqual(self.todo.read_bytes(), before)

    def test_a_readable_tidy_keeps_states_ids_history_and_quotes(self):
        before = (L1 / 'before.md').read_text(encoding='utf-8')
        self.assertEqual(self.states(L1_COMPLIANT), self.states(before))
        self.write(L1_COMPLIANT)
        unchanged = self.todo.read_bytes()
        self.assertNotEqual(record('tick', self.todo, 'T3', 'FINDINGS V2').returncode, 0)  # the bare ID names neither
        self.assertEqual(self.todo.read_bytes(), unchanged)
        result = record('tick', self.todo, 'D4/T3', 'FINDINGS V2')
        self.assertEqual(result.returncode, 0, result.stdout)
        changed = [line for line in self.todo.read_text(encoding='utf-8').splitlines() if line not in L1_COMPLIANT.splitlines()]
        self.assertEqual(changed, ['- [x] D4/T3 -- player uses shared formatter (supports A2); verified: FINDINGS V2'])
        for text in (before, (L1 / 'trial-after.md').read_text(encoding='utf-8'), L1_COMPLIANT):
            self.assertIn('removed by owner 2026-10-19 ("drop the widget")', text)
            self.assertNotIn('T0', self.states(text))  # removed history is not a live ticket

    def test_an_outstanding_human_check_is_missing_verification(self):
        self.write('- [x] T2 — shows Final; verified: FINDINGS V2; needs human: phone check\n')
        self.assertEqual(len(self.items.scan(self.task)['unbacked']), 1)
        self.write('### T2 — Shows Final\nStatus: implemented\nVerification: needs human — phone check\n')
        before = self.todo.read_bytes()
        self.assertNotEqual(record('tick', self.todo, 'T2', 'FINDINGS V2').returncode, 0)
        self.assertEqual(self.todo.read_bytes(), before)

    def test_stopped_work_is_paused_with_its_reason_apart_and_stays_unfinished(self):
        # P2 live test: the stop handoff wrote "Status: stopped (...)", which is not a listed ticket state.
        self.write((ROOT / 'tests/fixtures/p2-stop-handoff/trial-after.md').read_text(encoding='utf-8'))
        row = self.items.scan(self.task)
        self.assertEqual(row['done'], 1)
        self.assertIn('T2', row['unclear'][0])
        self.write('### T1 — Web path\nStatus: verified\nEvidence: FINDINGS V1\n\n### T2 — Run the build check\n'
                   'Status: paused\nPaused: owner stop, 2026-11-04: "Stop now. Cancel the running build check."\n'
                   'Verification: not run\n')
        row = self.items.scan(self.task)
        self.assertEqual((row['done'], row['unclear'], len(row['paused'])), (1, [], 1))
        before = self.todo.read_bytes()
        self.assertNotEqual(record('tick', self.todo, 'T2', 'FINDINGS V2').returncode, 0)
        self.assertEqual(self.todo.read_bytes(), before)
        rule = (ROOT / 'skills/workflow/TASK-FOLDER.md').read_text(encoding='utf-8')
        self.assertIn('`Status: paused` with the reason on its own line', rule)

    def test_resume_keeps_the_original_approval_quote(self):
        self.assertIn('Never rewrite the original `- Approval:` quote', (ROOT / 'skills/resume-task/SKILL.md').read_text(encoding='utf-8'))
        policy = (ROOT / 'skills/workflow/VISUAL-REVIEW.md').read_text(encoding='utf-8')
        self.assertIn('`- Reconfirmed (gate two): r<N>, <date>: "<words>"`', policy)
        self.assertIn('The original Approval quote stays unchanged', policy)

    def test_conflicting_status_lines_are_reported(self):
        self.write('### T1 — Check\nStatus: ready\nStatus: in progress\n')
        row = self.items.scan(self.task)
        self.assertEqual(row['open'], [])
        self.assertIn('conflicting Status lines', row['unclear'][0])


FORMAT = ROOT / 'tests/fixtures/todo-format-1920x1080'  # legacy.md: a real project TODO, sanitised (names and paths replaced; IDs, structure, states unchanged)
OVERVIEW = """# TODO

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| D4/T3 | Check both phones | Blocked | none |
| D4/T8 | Turn off anti-aliasing | Not started | D4/T3 |
| D3/T8 | Old fallback | Superseded | none |
| T9 | Wait for the owner | Paused | D4/T8 |

## Tickets

### D4/T8 — Turn off anti-aliasing
Status: Not started

What needs to happen: Select off when the phone gives less than requested.

How to verify:
- `npm test` passes.

Verification: not run

References:
- Depends on: D4/T3
- Evidence: none

### D4/T3 — Check both phones
Status: Blocked
Blocker: OnePlus not connected

How to verify:
- Human check: the owner compares both panels.

Verification: Samsung passed (V3); OnePlus not run

References:
- Depends on: none
- Evidence: FINDINGS V3

### T9 — Wait for the owner
Status: Paused
Paused: owner stop, 2026-11-04: "Stop for today."

References:
- Depends on: D4/T8

## History

### D3/T8 — Old fallback
Status: Superseded
Decision: Q21

References:
- Depends on: none
"""


class ReadableFormatTests(TicketFixture):
    """The owner's TODO format: overview table, then tickets with labelled sections. Status lines stay the source."""

    def parsed(self, text):
        lines = text.splitlines()
        found = self.items.tickets.parse(lines)
        return found, self.items.tickets.overview(lines, found)[1]

    def facts(self, text):
        """Per ticket: state, and every requirement, acceptance, decision, question, check and ticket ID it names."""
        lines = text.splitlines()
        return {t.qualified: (t.category, set(re.findall(r'\b[RADQVT]\d+\b', '\n'.join(lines[t.start:t.end]))))
                for t in self.items.tickets.parse(lines)}

    def test_the_real_legacy_todo_and_its_rewrite_record_the_same_facts(self):
        legacy = (FORMAT / 'legacy.md').read_text(encoding='utf-8')
        readable = (FORMAT / 'readable.md').read_text(encoding='utf-8')
        self.assertEqual({k: v[0] for k, v in self.facts(legacy).items()},
                         {'T1': 'done', 'T2': 'open', 'T3': 'open', 'T4': 'open'})
        self.assertEqual(self.facts(readable), self.facts(legacy))
        self.assertEqual(self.parsed(readable)[1], [])
        for text in (legacy, readable):  # the approval boundary and the D1 decision survive the rewrite
            self.assertIn('# Tickets (revision 1, proposed 2026-11-04)', text)
            self.assertIn('by: agent', text)
        self.assertNotIn(';', ''.join(line for line in readable.splitlines() if line.startswith('### ')))

    def test_legacy_checkbox_todo_still_ticks_as_before(self):
        legacy = (FORMAT / 'legacy.md').read_text(encoding='utf-8')
        self.write(legacy)
        result = record('tick', self.todo, 'T2', 'FINDINGS V2')
        self.assertEqual(result.returncode, 0, result.stdout)
        changed = [line for line in self.todo.read_text(encoding='utf-8').splitlines() if line not in legacy.splitlines()]
        self.assertEqual(len(changed), 1)
        self.assertTrue(changed[0].startswith('- [x] T2 — The server refuses') and changed[0].endswith('; verified: FINDINGS V2'))
        self.write(legacy)  # T4's needs-human check keeps it untickable, as before
        self.assertNotEqual(record('tick', self.todo, 'T4', 'FINDINGS V4').returncode, 0)

    def test_states_and_revision_qualified_ids_in_the_table(self):
        tickets, problems = self.parsed(OVERVIEW)
        self.assertEqual(problems, [])
        self.assertEqual({t.qualified: t.category for t in tickets},
                         {'D4/T8': 'open', 'D4/T3': 'blocked', 'T9': 'paused', 'D3/T8': 'closed'})
        self.write(OVERVIEW)
        row = self.items.scan(self.task)
        self.assertEqual((row['done'], row['overview'], row['unclear']), (0, [], []))

    def test_a_disagreeing_table_is_reported_and_never_decides_a_state(self):
        text = (OVERVIEW.replace('| D4/T8 | Turn off anti-aliasing | Not started | D4/T3 |',
                                 '| D4/T8 | Turn off anti-aliasing | Verified | none |')
                .replace('| T9 | Wait for the owner | Paused | D4/T8 |\n', '| T9 | Wait | Paused | D4/T8 |\n| T9 | Again | Paused | D4/T8 |\n'
                         '| T7 | Gone | Not started | none |\n| T3 | Short ID | Blocked | none |\n'))
        tickets, problems = self.parsed(text)
        messages = '\n'.join(p.message for p in problems)
        self.assertIn('D4/T8 at line 8 says Status "Verified" but the ticket says "Not started"', messages)
        self.assertIn('lists dependencies "none" but the ticket says "D4/T3"', messages)
        self.assertIn('T9 has 2 overview rows', messages)
        self.assertIn('overview row T7 at line 12 names no ticket', messages)
        self.assertIn('overview row T3 at line 13 names no ticket', messages)  # bare T3 is not D4/T3
        self.assertEqual({t.qualified: t.category for t in tickets}['D4/T8'], 'open')
        missing = OVERVIEW.replace('| D3/T8 | Old fallback | Superseded | none |\n', '')
        self.assertIn('D3/T8 (line', '\n'.join(p.message for p in self.parsed(missing)[1]))
        self.write(text)
        row = self.items.scan(self.task)
        self.assertEqual(row['done'], 0)
        self.assertEqual(len(row['overview']), 5)
        ambiguous = ('| Ticket | Status |\n|---|---|\n| T3 | Not started |\n\n## Revision D4\n### T3 — New\nStatus: Not started\n\n'
                     '## Revision D3\n### T3 — Old\nStatus: Superseded\n')
        self.assertEqual([p.message for p in self.parsed(ambiguous)[1]],
                         ['overview row T3 at line 3 is ambiguous (D4/T3, D3/T3); use the qualified ID'])

    def test_unlisted_or_checkbox_rows_and_tables_outside_the_format(self):
        text = ('| Ticket | Status |\n|---|---|\n| T1 | box checked |\n| T2 | Verified |\n| T4 | Ready |\n\n- [x] T2 — b; verified: V2\n\n'
                '### T1 — A\nStatus: box checked\n\n### T4 — C\nStatus: Ready\n')
        messages = '\n'.join(p.message for p in self.parsed(text)[1])
        self.assertIn('T1 at line 3 cannot be checked: the ticket\'s status is unreadable (Status "box checked"', messages)
        self.assertIn('summarises a checkbox ticket', messages)
        self.assertEqual(len(messages.splitlines()), 2)  # T4 agrees
        fenced = '```markdown\n| Ticket | Status |\n|---|---|\n| T5 | Verified |\n```\n| ID | State |\n|---|---|\n| T6 | done |\n\n### T1 — A\nStatus: ready\n'
        self.assertEqual(self.parsed(fenced)[1], [])

    def test_incomplete_verification_in_the_new_sections(self):
        base = ('### T1 — Device check\nStatus: Verified\n\nHow to verify:\n- `npm test` passes; an unavailable reading keeps the request.\n'
                '{human}\nVerification: {result}\n\n{owner}References:\n- Evidence: FINDINGS V1\n')
        cases = {('', 'passed', ''): 'done',  # expected-result wording under How to verify is not a result
                 ('', 'failed: npm test', ''): 'unbacked',
                 ('', 'passed\nVerification: not run', ''): 'unbacked',
                 ('- Human check: the owner looks at the panel.', 'passed', ''): 'unbacked',
                 ('- needs human: phone check', 'passed', 'Owner acceptance: none\n\n'): 'unbacked',
                 ('- Human check: the owner looks at the panel.', 'passed', 'Owner acceptance: not accepted yet\n\n'): 'unbacked',
                 ('- Human check: the owner looks at the panel.', 'passed', 'Owner acceptance: owner, 2026-11-05, V2\n\n'): 'done',
                 ('- [ ] Samsung panel', 'passed', ''): 'unbacked'}
        for (human, result, owner), category in cases.items():
            with self.subTest(human=human, result=result, owner=owner):
                self.assertEqual(self.parsed(base.format(human=human, result=result, owner=owner))[0][0].category, category)

    def test_tick_updates_the_status_line_and_its_overview_row_together(self):
        self.write(OVERVIEW.replace('Verification: not run\n', 'Verification: passed\n'))
        result = record('tick', self.todo, 'D4/T8', 'FINDINGS V8')
        self.assertEqual(result.returncode, 0, result.stdout)
        raw = self.todo.read_bytes()
        self.assertIn(b'| D4/T8 | Turn off anti-aliasing | Verified | D4/T3 |\r\n', raw)
        self.assertIn(b'### D4/T8 \xe2\x80\x94 Turn off anti-aliasing\r\nStatus: Verified\r\n', raw)
        self.assertIn(b'- Depends on: D4/T3\r\n- Evidence: FINDINGS V8\r\n', raw)
        self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))
        row = self.items.scan(self.task)
        self.assertEqual((row['done'], row['overview']), (1, []))

    def test_tick_refuses_while_the_row_disagrees_or_a_human_check_is_open(self):
        text = OVERVIEW.replace('Verification: not run\n', 'Verification: passed\n')
        self.write(text.replace('| Not started | D4/T3 |', '| In progress | D4/T3 |'))
        before = self.todo.read_bytes()
        result = record('tick', self.todo, 'D4/T8', 'FINDINGS V8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('overview table disagrees with D4/T8', result.stdout)
        self.assertEqual(self.todo.read_bytes(), before)
        human = ('### T1 — Look at it\nStatus: Implemented\n\nHow to verify:\n- Human check: the owner looks at the captures.\n\n'
                 'Verification: tests passed (V1)\n')
        self.write(human)
        before = self.todo.read_bytes()
        result = record('tick', self.todo, 'T1', 'FINDINGS V1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('human check with no Owner acceptance', result.stdout)
        self.assertEqual(self.todo.read_bytes(), before)
        self.write(human + 'Owner acceptance: owner, 2026-11-05: "looks right" (V2)\n')
        self.assertEqual(record('tick', self.todo, 'T1', 'FINDINGS V2').returncode, 0)

    def test_the_example_reads_as_it_says(self):
        text = (ROOT / 'skills/workflow/examples/readable-todo.md').read_text(encoding='utf-8')
        tickets, problems = self.parsed(text)
        self.assertEqual(problems, [])
        self.assertEqual({t.qualified: t.category for t in tickets}, {'T1': 'done', 'T2': 'blocked', 'T3': 'open'})
        rule = (ROOT / 'skills/workflow/TASK-FOLDER.md').read_text(encoding='utf-8')
        self.assertIn("each ticket's single `Status:` line is the source", rule)
        self.assertIn('`How to verify` lists planned checks only, never results', rule)


if __name__ == '__main__':
    unittest.main()
