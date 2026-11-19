"""verify-app (layer 1: drive an app and capture evidence) and reproduce-bug (the bug job on top of it).

Docs/plans/2026-11-18-bug-reproducer, T1 and T2. These checks prove the skill text states each rule;
whether an agent follows it is proven by the live tickets T4 to T7.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "skills" / "verify-app"
REPRODUCE = ROOT / "skills" / "reproduce-bug"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    return text.split("---", 2)[1]


class VerifyAppSkill(unittest.TestCase):
    def test_frontmatter_names_the_skill_and_allows_the_model_to_start_it(self):
        text = read(VERIFY / "SKILL.md")
        self.assertTrue(text.startswith("---\nname: verify-app\n"))
        self.assertIn("description:", frontmatter(text))
        self.assertNotIn("disable-model-invocation", frontmatter(text))

    def test_generated_skill_has_every_section_and_lives_under_claude_skills(self):
        text = read(VERIFY / "SKILL.md")
        self.assertIn(".claude/skills/verify-<app>/", text)
        for section in ("Launch", "Doctor", "Drive", "Evidence", "Cleanup", "Helpers", "Settings"):
            self.assertIn(f"- **{section}:**", text, section)
        self.assertIn("features/", text)

    def test_setup_check_has_nine_steps_and_a_draft_until_it_ran(self):
        text = read(VERIFY / "SKILL.md")
        section = text.split("## Setup check", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(len(re.findall(r"^\d+\. ", section, re.MULTILINE)), 9)
        self.assertIn("draft", section)
        self.assertIn("evidence", section.lower())

    def test_maintain_pass_has_three_outcomes_and_edits_only_its_own_folder(self):
        text = read(VERIFY / "SKILL.md")
        section = text.split("## Keep the map current", 1)[1].split("\n## ", 1)[0]
        for outcome in ("**clean**", "**changed**", "**blocked**"):
            self.assertIn(outcome, section)
        self.assertIn("only the verify skill's own folder", section)
        self.assertIn("product bug", section)
        self.assertNotIn("pull request", section.lower().replace("never a pull request", ""))


class ReproduceBugOrder(unittest.TestCase):
    def test_a_named_fix_goes_to_the_fix_check_before_any_drive(self):
        text = read(REPRODUCE / "SKILL.md")
        two = text.split("## 2.", 1)[1].split("\n## ", 1)[0]
        self.assertIn("go to [FIX-CHECK.md](FIX-CHECK.md) now", two)
        self.assertIn("no driver", two)
        self.assertIn("From Launch on, every way out goes through step 5", text)

    def test_doctor_runs_after_launch_and_a_named_commit_never_runs_on_local_changes(self):
        two = read(REPRODUCE / "SKILL.md").split("## 2.", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("- the verify skill's Doctor passes", two)
        self.assertLess(two.index("go to [FIX-CHECK.md](FIX-CHECK.md) now"), two.index("start the app there with its Launch, and run Doctor's second part"))
        self.assertIn("`git status --short --untracked-files=all` shows any change, untracked files included", two)
        self.assertIn("never stands in for the commit", two)
        self.assertIn("names a version or build but no commit gets its commit first", two)
        self.assertIn("one commit's Doctor never stands for the other", read(REPRODUCE / "FIX-CHECK.md"))

    def test_each_proof_starts_from_a_reset_and_a_different_wrong_state_is_reported(self):
        text = read(REPRODUCE / "SKILL.md")
        self.assertIn("Reset as the feature map says first, so the proof does not depend on what Explore did", text)
        self.assertIn("showed neither end state", text)
        self.assertIn("shows neither end state", read(REPRODUCE / "FIX-CHECK.md"))

    def test_setup_proves_the_driver_attaches_and_the_video_is_saved(self):
        self.assertIn("And prove the driver", read(VERIFY / "SKILL.md"))
        readme = read(VERIFY / "guard" / "README.md")
        self.assertIn("`drive.mjs <run> attach` and `drive.mjs <run> snapshot`", readme)
        self.assertIn("the session's video is in the run folder's `output/`", readme)
        self.assertIn("which proves the attached browser is the guarded one", readme)
        self.assertIn("a navigation to another host made from the attached driver fails", read(VERIFY / "SKILL.md"))
        self.assertIn("`drive.mjs <run> goto https://example.org/verify-guard-probe`", readme)
        self.assertIn("Content-Security-Policy cannot stop the probe", readme)
        self.assertNotIn("eval \"() => fetch(", readme)
        self.assertIn("every dependency manifest and lockfile", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("no installed package is a link into the repository itself", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("the machine settings file (`localFile`) and the artifacts folder are each ignored", readme)
        self.assertIn("the guard's own settings check passes (`node <skill>/run.mjs --list` from the repository root with a new `VERIFY_RUN` and `VERIFY_JOURNEYS=<skill>/journeys`", read(VERIFY / "SKILL.md"))
        self.assertIn("outside its `node_modules` (links that stay inside `node_modules`, such as `.bin`, are normal)", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("Run every verify command (Doctor, journeys, the driver) from the developer's checkout root", read(REPRODUCE / "FIX-CHECK.md"))

    def test_journeys_run_through_the_runner_and_the_pin_is_checked_before_launch(self):
        readme = read(VERIFY / "guard" / "README.md")
        self.assertIn("node .claude/skills/verify-<app>/run.mjs --grep-invert", readme)
        self.assertIn("node <skill>/run.mjs explore.spec.ts", readme)
        self.assertIn("never `npx playwright test` directly", readme)
        self.assertNotRegex(readme.replace("never `npx playwright test` directly", ""), r"npx playwright test")
        self.assertIn("must print only loopback addresses", readme)
        self.assertIn("a pinned backend name resolves only to this machine", read(VERIFY / "SKILL.md"))
        self.assertIn("inside its container or virtual machine when it runs in one", readme)
        self.assertIn("run `node <skill>/run.mjs --list` with `VERIFY_SETTINGS` on the copy", readme)
        self.assertIn("never a command or setting that opens a browser", read(VERIFY / "SKILL.md"))
        self.assertIn("It starts the dev server with no outbound proxy", read(VERIFY / "SKILL.md"))
        self.assertIn("`NODE_USE_ENV_PROXY`", read(VERIFY / "SKILL.md"))
        self.assertIn("names a blocked production host (search them for each blocked host;", read(VERIFY / "SKILL.md"))
        self.assertIn("the guard never sees it", read(VERIFY / "guard" / "README.md"))
        self.assertIn("except a name the owner points at this machine and pins", read(VERIFY / "guard" / "README.md"))
        self.assertIn("which the guard accepts only with a pin", read(VERIFY / "guard" / "README.md"))
        self.assertIn("add it there in the copy only", read(VERIFY / "guard" / "README.md"))
        self.assertIn("so its login is not hidden from the run's output or files", read(VERIFY / "guard" / "README.md"))
        self.assertIn("The run does not hide this login from its output or files", read(VERIFY / "SKILL.md"))
        self.assertIn("`git check-ignore -q` succeeds for the login file, the machine settings file (`localFile`) and the artifacts folder (checked as", read(VERIFY / "SKILL.md"))
        self.assertNotIn("locator.evaluate", read(VERIFY / "guard" / "README.md"))
        self.assertIn("a capture or log that shows it is fine", read(VERIFY / "guard" / "README.md"))
        self.assertIn("its e-mail must be a throwaway alias that belongs to no person", read(VERIFY / "SKILL.md"))
        self.assertIn("until they do, stop here", read(VERIFY / "SKILL.md"))
        self.assertIn("may name a host listed as a `rewrite` source", read(VERIFY / "SKILL.md"))
        self.assertIn("step 5 says (the dependency link removed as a link first, then its ownership check", read(REPRODUCE / "SKILL.md"))
        self.assertIn("shows nothing besides the build output this run made and recorded", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("--untracked-files=all --ignored` shows nothing besides the dependency link", read(REPRODUCE / "FIX-CHECK.md"))

    def test_doctor_reads_the_checkout_before_launch_once_per_checkout(self):
        skill = read(VERIFY / "SKILL.md")
        self.assertIn("**Before Launch**, on the checkout about to start", skill)
        self.assertIn("Doctor's first part must have passed on this checkout", skill)
        self.assertIn("server-side rendering", read(VERIFY / "guard" / "README.md"))
        two = read(REPRODUCE / "SKILL.md").split("## 2.", 1)[1].split("\n## ", 1)[0]
        self.assertIn("never a second time here", two)
        fix = read(REPRODUCE / "FIX-CHECK.md")
        self.assertLess(fix.index("Run the first part of the verify skill's Doctor for the worktree"), fix.index("Then start the app from the worktree"))

    def test_a_leftover_worktree_is_removed_only_after_proof_of_ownership(self):
        text = read(REPRODUCE / "FIX-CHECK.md")
        self.assertIn("belongs to an earlier run of this job", text)
        self.assertIn("no dev server or process is using it", text)
        self.assertIn("as step 5 says", text)
        self.assertIn("add a line with its exact path, its commit and the run's name to `<artifacts>/worktrees.md`", text)
        self.assertIn("never a run folder", text)
        self.assertIn("The port must be free first", text)
        self.assertIn("<artifacts>/worktrees/<name> <commit>", text)
        self.assertNotIn("<artifacts>/<name>", text)

    def test_generated_skills_launch_on_a_free_port_delete_accidental_captures_and_cli_files(self):
        text = read(VERIFY / "SKILL.md")
        self.assertIn("and the port must be free: nothing listens on it", text)
        self.assertIn("not an HTTP request", text)
        self.assertIn("every dev server proxy target and every backend address the dev server itself calls", text)
        self.assertIn("refuse when any target is not the allowed backend", read(VERIFY / "guard" / "README.md"))
        self.assertIn("nothing listens on the port", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("The throwaway test account's own e-mail and name may appear in captures", text)
        readme = read(VERIFY / "guard" / "README.md")
        self.assertIn("never decide on `-v`, which also exits 0 for a path a `!` rule re-includes", readme)
        self.assertIn("2. First do step 3's check, before the machine settings file or the login file holds anything", readme)
        self.assertIn("never leaves the guarded Chromium", readme)
        self.assertIn("refusing every other option", readme)
        self.assertIn("delete that run's whole folder `<artifacts>/<run>/`", read(VERIFY / "SKILL.md"))
        self.assertIn("goes to `testInfo.outputPath('<name>.png')`", read(VERIFY / "GUIDE.md"))
        self.assertIn("goes to `testInfo.outputPath('<name>.png')`", read(REPRODUCE / "SKILL.md"))
        self.assertIn("`@playwright/test` is 1.65 or newer", read(VERIFY / "guard" / "README.md"))
        self.assertIn("the installed `@playwright/test` is 1.65 or newer", read(VERIFY / "SKILL.md"))
        self.assertIn("an uncommitted edit must never be credited to the fix", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("Fix confirmed needs the correct end state on both fix runs", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("the outcome comes only from this file's Report section, never Could not reproduce", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("on the developer's checkout, where the verify files and evidence live, every time", read(VERIFY / "SKILL.md"))
        self.assertIn("`Status: ready (setup check passed <date>, <commit>)`", read(VERIFY / "SKILL.md"))
        self.assertIn("whose SKILL.md says `Status: ready`", read(REPRODUCE / "SKILL.md"))
        self.assertIn("for an origin the path needs (the app's API, a backend, a `rewrite` source, a sign-in provider, a page the path redirects to)", read(REPRODUCE / "SKILL.md"))
        self.assertIn("has a `blocked`, `failed` or `escaped` line", read(REPRODUCE / "SKILL.md"))
        self.assertIn("a run with a `blocked`, `failed` or `escaped` line", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("SKILL.md step 3's `network.log` rule applies to every run on both commits", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("a third-party origin such as analytics, ads or fonts does not matter", read(REPRODUCE / "SKILL.md"))
        self.assertIn("1. Run Doctor's first part, then start the app with Launch.", read(VERIFY / "SKILL.md"))
        self.assertIn("and where the local backend runs when it calls that name itself", read(VERIFY / "SKILL.md"))
        self.assertIn("On the developer's checkout, do what step 4 of \"Run an older commit\" does for a worktree: stop the baseline's server", read(REPRODUCE / "FIX-CHECK.md"))
        self.assertIn("or its two runs differed", read(REPRODUCE / "SKILL.md"))
        self.assertIn("follow the same rules in `guardRequests`", readme)
        self.assertIn("Every proof run of this journey, the first included", read(REPRODUCE / "SKILL.md"))
        self.assertIn("Study by reading only: never run the app, its dev server or its start command in this step", read(VERIFY / "SKILL.md"))
        self.assertIn("sets `VERIFY_JOURNEYS=<artifacts>/journeys/<first run>` explicitly in its own command", read(REPRODUCE / "SKILL.md"))
        self.assertNotIn("showing the test account's personal data", text)
        self.assertIn("checked as `<artifacts>/` with a trailing slash", text)
        self.assertIn("`<artifacts>/` with a trailing slash so a folder-only rule matches", read(VERIFY / "guard" / "README.md"))
        fix = read(REPRODUCE / "FIX-CHECK.md")
        self.assertLess(fix.index("`git check-ignore -q <artifacts>/` succeeds"), fix.index("Then make a separate worktree"))
        self.assertIn("delete its `.playwright-cli` folder", text)


class StepByStep(unittest.TestCase):
    def test_verify_app_drive_has_explore_then_journey(self):
        text = read(VERIFY / "SKILL.md")
        drive = text.split("- **Drive:**", 1)[1].split("\n- **Evidence:**", 1)[0]
        for item in ("one action at a time", "drive.mjs <run> attach", "snapshot", "journey"):
            self.assertIn(item, drive, item)

    def test_reproduce_bug_explores_then_proves_twice(self):
        text = read(REPRODUCE / "SKILL.md")
        section = text.split("## 3.", 1)[1].split("\n## ", 1)[0]
        for item in ("**Explore.**", "**Prove.**", "one action at a time", "what changed", "twice"):
            self.assertIn(item, section, item)
        self.assertIn("proof runs on both commits", read(REPRODUCE / "FIX-CHECK.md"))

    def test_guard_readme_documents_the_explore_session(self):
        readme = read(VERIFY / "guard" / "README.md")
        for item in ("## Explore step by step", "explore.spec.ts", "prepare.ts", "stop", "VERIFY_EXPLORE_MINUTES"):
            self.assertIn(item, readme, item)

    def test_guide_names_test_agents_as_a_later_base(self):
        self.assertIn("Playwright Test Agents", read(VERIFY / "GUIDE.md"))


class VerifyAppGuide(unittest.TestCase):
    def test_part_one_adds_a_screen_to_the_map(self):
        text = read(VERIFY / "GUIDE.md")
        part = text.split("## Part 1", 1)[1].split("## Part 2", 1)[0]
        for item in ("FEATURE-MAP.md", "setup check", "verify-app", "Gotchas", "Preconditions", "Explore step by step",
                     "drive.mjs"):
            self.assertIn(item, part, item)

    def test_part_two_adds_a_job_that_uses_only_layer_one_and_keeps_the_guard(self):
        text = read(VERIFY / "GUIDE.md")
        part = text.split("## Part 2", 1)[1]
        for item in ("input", "rules", "outcome words", "evidence", "guard", ".claude-plugin/plugin.json",
                     "tests/"):
            self.assertIn(item, part, item)
        self.assertIn("never drives the app another way", part)
        self.assertIn("not built", part)

    def test_feature_map_template_has_the_four_sections_and_names_preconditions_and_evidence(self):
        text = read(VERIFY / "FEATURE-MAP.md")
        for heading in ("## Sub-features", "## How to get to it", "## Driving it", "## Gotchas"):
            self.assertIn(heading, text)
        for item in ("Preconditions:", "Evidence:", "State check:"):
            self.assertIn(item, text)


class ReproduceBugSkill(unittest.TestCase):
    OUTCOMES = ("**Reproduced**", "**Could not reproduce**", "**Blocked**", "**Fix confirmed**", "**Fix not confirmed**")

    def test_frontmatter_and_it_builds_on_the_verify_skill(self):
        text = read(REPRODUCE / "SKILL.md")
        self.assertTrue(text.startswith("---\nname: reproduce-bug\n"))
        self.assertNotIn("disable-model-invocation", frontmatter(text))
        self.assertIn("verify-app", text)
        self.assertIn(".claude/skills/verify-<app>/", text)

    def test_states_exactly_the_five_outcomes(self):
        text = read(REPRODUCE / "SKILL.md")
        section = text.split("## Outcomes", 1)[1].split("\n## ", 1)[0]
        for outcome in self.OUTCOMES:
            self.assertIn(outcome, section, outcome)
        self.assertEqual(len(re.findall(r"^- \*\*", section, re.MULTILINE)), 5)

    def test_input_missing_detail_gives_one_question_and_no_run(self):
        text = read(REPRODUCE / "SKILL.md")
        section = text.split("## 1.", 1)[1].split("\n## ", 1)[0]
        for item in ("steps", "expected", "actual", "commit", "platform", "one question"):
            self.assertIn(item, section, item)
        self.assertIn("A missing commit means the developer's current checkout", section)

    def test_fails_closed_without_verify_skill_setup_check_or_map_section(self):
        text = read(REPRODUCE / "SKILL.md")
        for item in ("setup check", "not mapped", "never a guess"):
            self.assertIn(item, text, item)

    def test_reproduce_twice_with_reset_state_check_and_second_look(self):
        text = read(REPRODUCE / "SKILL.md")
        section = text.split("## 3.", 1)[1].split("\n## ", 1)[0].lower()
        for item in ("twice", "reset", "read-only", "second look", "correct end state", "broken end state"):
            self.assertIn(item, section, item)
        self.assertIn("never set internal state", section)

    def test_fix_check_needs_a_baseline_and_the_same_backend(self):
        text = read(REPRODUCE / "FIX-CHECK.md")
        for item in ("commit before the fix", "twice", "no baseline", "same backend", "Fix confirmed",
                     "Fix not confirmed"):
            self.assertIn(item, text, item)

    def test_old_commits_run_in_a_worktree_and_the_link_is_removed_as_a_link(self):
        text = read(REPRODUCE / "FIX-CHECK.md") + read(REPRODUCE / "SKILL.md")
        for item in ("git worktree add", "git worktree remove", "removed as a link", "working copy is never touched",
                     'cmd /c rmdir "<worktree>\\node_modules"'):
            self.assertIn(item, text, item)
        self.assertNotRegex(text, r"rm -rf|Remove-Item -Recurse")

    def test_no_fix_step(self):
        text = read(REPRODUCE / "SKILL.md")
        self.assertIn("never changes the app's code", text)
        self.assertNotRegex(text.lower(), r"open a (draft )?pull request|write the fix|attempt a fix")


JOB_WORDS = re.compile(r"reproduc|bug report|fix commit|fix confirmed|could not reproduce", re.IGNORECASE)
SOURCE_OR_COMPANY = re.compile(
    r"pstack|Lauren Tan|cursor/plugins|\bCursor\b|\bSlack\b|github\.com|\bbenny\b|\bAXA\b|axastudios|cheflabels|"
    r"pletrix|labeler|mulcol|hooqd|polyseam",
    re.IGNORECASE,
)


def skill_files(folder: Path):
    return [p for p in folder.rglob("*") if p.is_file() and p.name != "LICENSE"]


class Ownership(unittest.TestCase):
    def test_layer_one_holds_no_job_words(self):
        layer_one = [VERIFY / "SKILL.md", VERIFY / "FEATURE-MAP.md", *sorted((VERIFY / "guard").iterdir())]
        for path in layer_one:
            self.assertIsNone(JOB_WORDS.search(read(path)), path.name)

    def test_no_source_or_company_names_outside_the_licence(self):
        for folder in (VERIFY, REPRODUCE):
            for path in skill_files(folder):
                match = SOURCE_OR_COMPANY.search(read(path))
                self.assertIsNone(match, f"{path.relative_to(ROOT)}: {match and match.group(0)}")

    def test_each_skill_keeps_the_mit_licence_and_a_codex_card(self):
        for folder in (VERIFY, REPRODUCE):
            self.assertIn("MIT License", read(folder / "LICENSE"), folder.name)
            card = read(folder / "agents" / "openai.yaml")
            self.assertIn("display_name:", card)
            self.assertNotIn("allow_implicit_invocation: false", card)

    def test_links_stay_inside_each_skill_folder(self):
        for folder in (VERIFY, REPRODUCE):
            for path in folder.rglob("*.md"):
                for target in re.findall(r"\]\(([^)#]+)\)", read(path)):
                    resolved = (path.parent / target).resolve()
                    self.assertTrue(resolved.exists(), f"{path.name} -> {target}")
                    self.assertTrue(resolved.is_relative_to(folder.resolve()), f"{path.name} -> {target}")


class Guard(unittest.TestCase):
    def guard(self) -> str:
        return read(VERIFY / "guard" / "guard.ts")

    def config(self) -> str:
        return read(VERIFY / "guard" / "playwright.config.ts")

    def test_guard_refuses_production_and_unset_backends_before_the_browser(self):
        text = self.guard()
        self.assertIn("if (blockedHosts.includes(backendHost))", text)
        self.assertIn("is a production host; refusing to start", text)
        self.assertIn("no backend is set; refusing to start", text)
        self.assertIn("export const settings = loadSettings();", text)
        self.assertIn("from './guard'", self.config())

    def test_browser_resolves_only_this_machine_and_the_allowed_backend(self):
        self.assertIn("`--host-resolver-rules=${pin}MAP * ~NOTFOUND, ", self.guard())
        config = self.config()
        self.assertIn("args: [hostResolverRule(), '--no-proxy-server']", config)
        self.assertIn("browserName: 'chromium'", config)

    def test_guard_blocks_and_logs_every_other_request_and_socket(self):
        text = self.guard()
        self.assertIn("log('blocked', `${route.request().method()} ${url.origin}`);", text)
        self.assertIn("return route.abort('blockedbyclient');", text)
        self.assertIn("context.routeWebSocket(", text)
        self.assertIn("log('blocked', `WEBSOCKET ${httpOrigin}`);", text)

    def test_the_log_never_holds_a_path_or_query(self):
        text = self.guard()
        for leak in ("${url.href}", "${socket.url()}", "${request.url()} (redirect", "-> ${rewritten}"):
            self.assertNotIn(leak, text.split("function log(", 1)[1], leak)
        self.assertNotIn("!settings.rewrite[origin] &&", text)
        self.assertIn("serviceWorkers: 'block'", self.config())

    def test_a_pinned_backend_resolves_only_to_this_machine(self):
        text = self.guard()
        self.assertIn("MAP ${new URL(settings.backend).hostname} ${pinTarget}", text)
        self.assertIn("settings.pinBackendTo.includes(':') ? `[${settings.pinBackendTo}]` : settings.pinBackendTo", text)
        self.assertIn("pinBackendTo must be a loopback address", text)
        setup = read(VERIFY / "guard" / "global-setup.ts")
        self.assertIn("lookup(host, { all: true })", setup)
        self.assertIn("does not resolve to this machine; refusing to start", setup)
        self.assertIn("globalSetup: './global-setup.ts'", self.config())
        self.assertIn("VERIFY_PIN_BACKEND_TO=", read(VERIFY / "guard" / "verify.local.example"))

    def test_rewrite_goes_only_to_the_backend_and_never_follows_redirects(self):
        text = self.guard()
        self.assertIn("rewrite is a list of origins", text)
        self.assertIn("rewrite[originOf(from, 'rewrite source')] = backend;", text)
        self.assertIn("route.fetch({ url: rewritten, maxRedirects: 0 })", text)

    def test_a_failed_rewrite_is_logged_by_origin_and_aborted(self):
        text = self.guard()
        self.assertIn("log('failed', `${route.request().method()} ${url.origin} -> ${target}`);", text)
        self.assertIn("return route.abort('failed');", text)
        self.assertIn("'rewritten' | 'blocked' | 'escaped' | 'failed'", text)

    def test_a_redirect_hop_outside_the_allowed_origins_fails_the_run(self):
        text = self.guard()
        self.assertIn("context.on('request'", text)
        self.assertIn("request.redirectedFrom()", text)
        self.assertIn("log('escaped'", text)
        self.assertIn("this run's evidence does not count", text)

    def test_helpers_are_found_through_the_skill_folder_in_any_module_system(self):
        self.assertFalse((VERIFY / "guard" / "global-teardown.ts").exists())
        for name in ("guard.ts", "global-setup.ts", "explore.spec.ts", "playwright.config.ts"):
            self.assertNotIn("__dirname", read(VERIFY / "guard" / name), name)
        self.assertIn("export const skillFolder = process.env.VERIFY_SKILL || dirname(resolve(process.env.VERIFY_SETTINGS", self.guard())
        explore = read(VERIFY / "guard" / "explore.spec.ts")
        self.assertIn("join(skillFolder, 'drive.mjs')", explore)
        self.assertIn("join(skillFolder, 'redact.mjs')", explore)

    def test_failed_requests_to_allowed_origins_are_logged(self):
        text = self.guard().split("async function guardContext", 1)[1]
        self.assertIn("context.on('requestfailed', (request) => {", text)
        self.assertIn("['net::ERR_BLOCKED_BY_CLIENT', 'net::ERR_ABORTED'].includes(reason)", text)
        self.assertIn("log('failed', `${request.method()} ${url.origin}`);", text)

    def test_contexts_a_journey_opens_itself_are_guarded_too(self):
        text = self.guard()
        self.assertIn("browser.newContext = async (options) => {", text)
        self.assertIn("await guardContext(made);", text)
        self.assertIn("browser.newPage = async (options) => {", text)
        self.assertIn("if (guardedContexts.has(context)) {", text)
        self.assertIn("browser: [async ({ browser }, use) => {\n    guardBrowser(browser);", text)
        self.assertIn("}, { scope: 'worker' }],", text)
        self.assertIn("}, { auto: true }],", text)
        self.assertIn("Every screenshot or file a journey writes itself, the setup check's included", read(VERIFY / "SKILL.md"))
        self.assertIn("a journey writes every screenshot or file itself to `testInfo.outputPath('<name>')`", read(VERIFY / "guard" / "README.md"))
        self.assertIn("guardRequests(context.request", text.split("async function guardContext", 1)[1])

    def test_the_report_device_is_set_for_explore_and_every_proof_run(self):
        config = self.config()
        self.assertIn("process.env.VERIFY_DEVICE", config)
        self.assertIn("process.env.VERIFY_VIEWPORT", config)
        self.assertIn("VERIFY_DEVICE must be desktop or mobile", config)
        self.assertIn("userAgent: mobile ? devices['Pixel 7'].userAgent : undefined", config)
        self.assertIn("devices[device === 'mobile' ? 'Pixel 7' : 'Desktop Chrome'].viewport", config)
        self.assertIn("in the environment variables of the commands that start it and the local backend", read(VERIFY / "SKILL.md"))
        skill = read(REPRODUCE / "SKILL.md")
        self.assertIn("set `VERIFY_DEVICE=desktop` or `mobile` and `VERIFY_VIEWPORT=<width>x<height>` on the explore command and on every proof run", skill)
        self.assertNotIn("test.use({ viewport", skill)

    def test_screenshot_baselines_go_to_the_run_folder(self):
        self.assertIn("snapshotPathTemplate: `${runFolder}/snapshots/{testFilePath}/{arg}{ext}`", self.config())

    def test_the_browser_never_uses_a_proxy(self):
        self.assertIn("launchOptions: { args: [hostResolverRule(), '--no-proxy-server'] }", self.config())
        self.assertIn("--no-proxy-server", read(VERIFY / "guard" / "README.md"))

    def test_login_only_from_the_ignored_file_and_no_trace(self):
        text = self.guard()
        self.assertIn("const values = readKeyValues(file);", text.split("export function readLogin", 1)[1])
        self.assertNotRegex(text, r"password\s*[:=]\s*['\"][^'\"]+['\"]")
        self.assertIn("trace: 'off'", self.config())
        self.assertIn("timeout: 180_000", self.config())

    def test_each_run_keeps_its_own_folder(self):
        text = self.guard()
        self.assertIn("VERIFY_RUN must name this run", text)
        self.assertIn("already exists; give this run a new VERIFY_RUN name", text)
        self.assertIn("process.env.TEST_WORKER_INDEX === undefined", text)
        self.assertIn("export const runFolder = join(settings.artifacts, settings.run);", text)
        self.assertIn("outputDir: `${runFolder}/output`", self.config())

    def test_explore_shares_the_guarded_logged_in_browser_and_stops_cleanly(self):
        text = read(VERIFY / "guard" / "explore.spec.ts")
        self.assertIn("from '../guard'", text)
        self.assertNotIn("from '@playwright/test'", text)
        self.assertIn("await prepare(page, login);", text)
        self.assertIn("browser.bind(session", text)
        self.assertIn("${settings.run} attach", text)
        self.assertIn("existsSync(stopFile)", text)
        self.assertIn("test.setTimeout(", text)
        self.assertNotRegex(text, r"login\.password[^;]*writeFileSync|console\.log\([^)]*password")
        self.assertIn("export async function prepare", read(VERIFY / "guard" / "prepare.example.ts"))

    def test_pinned_backend_is_not_excluded_from_the_resolver_map(self):
        text = self.guard()
        self.assertIn("...(settings.pinBackendTo ? [] : [new URL(settings.backend).hostname]),", text)
        self.assertIn("a pinned backend cannot be combined with rewrite", text)

    def test_run_name_and_run_folder_are_claimed_fresh(self):
        text = self.guard()
        self.assertIn(r"/^(?!\.{1,2}$)[A-Za-z0-9._-]+$/", text)
        self.assertIn("mkdirSync(claimed, { recursive: false })", text)
        self.assertIn("already exists; give this run a new VERIFY_RUN name", text)

    def test_explore_reports_how_it_ended_and_fails_unless_stopped(self):
        text = read(VERIFY / "guard" / "explore.spec.ts")
        self.assertIn("browser.bind(session, { workspaceDir: runFolder })", text)
        self.assertIn("while (!existsSync(stopFile) && Date.now() < deadline && !page.isClosed())", text)
        self.assertIn("VERIFY_EXPLORE_MINUTES must be a whole number from 1 to 120", text)
        self.assertIn("ended: ${ended}", text)
        self.assertIn("throw new Error(`explore session ${ended}", text)
        self.assertIn("drive.mjs", text)

    def test_drive_allows_only_screen_actions_and_read_only_looks(self):
        text = read(VERIFY / "guard" / "drive.mjs")
        for allowed in ("'snapshot'", "'click'", "'fill'", "'screenshot'", "'attach'", "'press'"):
            self.assertIn(allowed, text, allowed)
        for refused in ("run-code", "unroute", "state-save", "request-body", "network-state-set", "tracing-start"):
            self.assertNotIn(f"'{refused}'", text.split("const ALLOWED", 1)[1].split("]);", 1)[0], refused)
        self.assertIn("is not allowed through the verify driver", text)
        self.assertIn("cwd: runFolder", text)
        self.assertIn("-s=${session}", text)

    def test_pinned_host_is_removed_from_the_final_exclusions(self):
        self.assertIn("if (settings.pinBackendTo) {\n    reachable.delete(new URL(settings.backend).hostname);\n  }", self.guard())

    def test_readme_names_every_driver_command_as_the_driver_spells_it(self):
        import re
        drive = read(VERIFY / "guard" / "drive.mjs")
        allowed = re.findall(r"'([a-z-]+)'", drive.split("const ALLOWED", 1)[1].split("]);", 1)[0])
        readme = read(VERIFY / "guard" / "README.md")
        listed = readme.split("The driver allows only screen actions and read-only looks: ", 1)[1].split(". ", 1)[0]
        for command in allowed:
            if command.startswith("mouse"):
                continue
            self.assertIn(command, listed, command)

    def test_driver_takes_no_options_and_checks_the_live_session(self):
        text = read(VERIFY / "guard" / "drive.mjs")
        self.assertIn("rest.some((arg) => arg.startsWith('-'))", text)
        self.assertIn("options are not allowed through the verify driver", text)
        self.assertIn("existsSync(join(runFolder, 'explore-result.md'))", text)
        self.assertIn("goto only takes an http or https address", text)
        self.assertNotIn("'console'", text.split("const ALLOWED", 1)[1].split("]);", 1)[0])

    def test_explore_unbinds_then_cleans_with_the_shared_module(self):
        explore = read(VERIFY / "guard" / "explore.spec.ts")
        self.assertNotIn("withoutQueries", explore)
        self.assertNotIn("? 'lost its page'", explore)
        finally_block = explore.split("} finally {", 1)[1]
        self.assertLess(finally_block.index("await browser.unbind()"), finally_block.index("redact.mjs"))
        self.assertLess(finally_block.index("redact.mjs"), finally_block.index("explore-result.md"))
        self.assertIn("ended = 'could not unbind the shared browser'", explore)
        self.assertIn("ended = 'could not clean the CLI files'", explore)
        self.assertLess(explore.index("if (page.isClosed())"), explore.index("} else if (existsSync(stopFile))"))
        self.assertIn("from './redact.mjs'", read(VERIFY / "guard" / "drive.mjs"))

    def test_explore_records_every_ending(self):
        text = read(VERIFY / "guard" / "explore.spec.ts")
        self.assertIn("ended = 'setup failed'", text)
        self.assertIn("test.afterEach(() => {", text)
        self.assertIn("finally {", text)
        self.assertIn("setTimeout(resolve, 1000)", text)

    def test_machine_values_come_from_an_untracked_local_file(self):
        text = self.guard()
        for key in ("VERIFY_BACKEND", "VERIFY_PIN_BACKEND_TO", "VERIFY_DEV_SERVER", "localFile"):
            self.assertIn(key, text, key)
        self.assertIn("is missing; copy", text)
        example = read(VERIFY / "guard" / "settings.example.json")
        self.assertNotIn('"backend"', example)
        self.assertIn('"localFile"', example)
        self.assertIn("VERIFY_BACKEND=", read(VERIFY / "guard" / "verify.local.example"))

    def test_a_named_backend_needs_a_pin_and_hosts_are_normalised(self):
        text = self.guard()
        self.assertIn("needs VERIFY_PIN_BACKEND_TO", text)
        self.assertIn(r".replace(/\.$/, '')", text)

    def test_explore_binds_a_unique_session_the_driver_reads(self):
        explore = read(VERIFY / "guard" / "explore.spec.ts")
        self.assertIn("const session = `${settings.run}-${process.pid}-${Date.now()}`;", explore)
        self.assertIn("Session: ${session}", explore)
        self.assertIn("from '../guard'", explore)
        drive = read(VERIFY / "guard" / "drive.mjs")
        self.assertIn(r"/^Session: (\S+)$/m", drive)
        self.assertIn("-s=${session}", drive)

    def test_settings_example_and_readme(self):
        settings = read(VERIFY / "guard" / "settings.example.json")
        for key in ("devServer", "blockedHosts", "rewrite", "loginFile", "loginKeys", "viewport",
                    "isMobile", "hasTouch", "artifacts", "localFile"):
            self.assertIn(f'"{key}"', settings, key)
        readme = read(VERIFY / "guard" / "README.md")
        for item in ("settings.json", "VERIFY_RUN", "## Limits", "proxy", "Cookies", "cuts query strings and fragments",
                     "console logs are deleted", "$env:VERIFY_JOURNEYS", "`redact.mjs`"):
            self.assertIn(item, readme, item)

if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(__import__("shutil").which("node"), "node is not installed")
class DriverBehaviour(unittest.TestCase):
    def drive(self, *args):
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            return subprocess.run(["node", str(VERIFY / "guard" / "drive.mjs"), *args], cwd=tmp,
                                  capture_output=True, text=True, env=dict(__import__("os").environ))

    def test_refuses_a_command_outside_the_allowlist(self):
        result = self.drive("run-1", "run-code", "x")
        self.assertEqual(result.returncode, 2)
        self.assertIn("is not allowed through the verify driver", result.stderr)

    def test_refuses_options(self):
        result = self.drive("run-1", "attach", "--config", "x.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("options are not allowed", result.stderr)

    def test_refuses_goto_without_http(self):
        result = self.drive("run-1", "goto", "file:///etc/passwd")
        self.assertEqual(result.returncode, 2)
        self.assertIn("goto only takes an http or https address", result.stderr)

    def test_refuses_a_bad_run_name(self):
        result = self.drive("..", "snapshot")
        self.assertEqual(result.returncode, 2)
        self.assertIn("is not a run name", result.stderr)



    def runner(self, *args):
        import json, os, subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cli = root / "node_modules" / "@playwright" / "test"
            cli.mkdir(parents=True)
            (cli / "cli.js").write_text(self.STUB_TEST_CLI, encoding="utf-8")
            skill = root / "skill"
            skill.mkdir()
            elsewhere = root / "artifacts" / "proof-input"
            elsewhere.mkdir(parents=True)
            (elsewhere / "settings.json").write_text(json.dumps({"artifacts": "artifacts", "loginFile": "login.env",
                                                                 "loginKeys": {"user": "U", "password": "P"}}), encoding="utf-8")
            (root / "login.env").write_text("U=tester@example.invalid\nP=fictional-pass-1\n", encoding="utf-8")
            for name in ("run.mjs", "redact.mjs"):
                (skill / name).write_bytes((VERIFY / "guard" / name).read_bytes())
            env = dict(os.environ, VERIFY_SETTINGS=str(elsewhere / "settings.json"), HTTPS_PROXY="http://127.0.0.1:9", PW_TEST_CONNECT_WS_ENDPOINT="ws://remote.example:9")
            return subprocess.run(["node", str(skill / "run.mjs"), *args], cwd=tmp, capture_output=True, text=True, env=env)


    def test_the_runner_allows_its_listed_options(self):
        result = self.runner("doctor.spec.ts", "--grep-invert", "explore:", "--repeat-each=2", "--list", "--headed")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("--grep-invert explore: --repeat-each=2 --list --headed", result.stdout)

    def test_the_runner_refuses_reporters_traces_and_the_ui(self):
        for flag in ("--reporter=html", "--trace", "--ui", "--config=x.ts", "--ui-port=9323", "--ui-host=0.0.0.0",
                     "--browser=firefox", "--project=webkit", "--update-snapshots", "-u", "--headed-debug",
                     "--add-reporter=html", "--last-failed-file=x.json", "--update-source-method=overwrite", "--anything-new"):
            result = self.runner("doctor.spec.ts", flag)
            self.assertEqual(result.returncode, 2, flag)
            self.assertIn("is not allowed through the verify runner", result.stderr, flag)

    def test_the_driver_finds_playwright_through_its_test_package(self):
        import json, os, subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "node_modules" / "@playwright" / "test"
            package.mkdir(parents=True)
            (package / "package.json").write_text('{"name":"@playwright/test","version":"0.0.0"}', encoding="utf-8")
            nested = package / "node_modules" / "playwright"
            nested.mkdir(parents=True)
            (nested / "package.json").write_text('{"name":"playwright","version":"0.0.0","exports":{".":"./index.js","./package.json":"./package.json"}}', encoding="utf-8")
            (nested / "cli.js").write_text("console.log('nested cli ' + process.argv.slice(2).join(' '));", encoding="utf-8")
            run_folder = root / "artifacts" / "run-1"
            run_folder.mkdir(parents=True)
            (run_folder / "explore.md").write_text("Session: run-1-1-1\n", encoding="utf-8")
            (root / "settings.json").write_text(json.dumps({"artifacts": "artifacts"}), encoding="utf-8")
            env = dict(os.environ, VERIFY_SETTINGS=str(root / "settings.json"))
            result = subprocess.run(["node", str(VERIFY / "guard" / "drive.mjs"), "run-1", "snapshot"], cwd=tmp,
                                    capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nested cli cli -s=run-1-1-1 snapshot", result.stdout)

    def test_queries_and_fragments_are_cut_without_touching_ordinary_text(self):
        import json, os, subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "node_modules" / "playwright").mkdir(parents=True)
            (root / "node_modules" / "playwright" / "cli.js").write_text(self.STUB_CLI, encoding="utf-8")
            run_folder = root / "artifacts" / "run-1"
            run_folder.mkdir(parents=True)
            (run_folder / "explore.md").write_text("Session: run-1-1-1\n", encoding="utf-8")
            (root / "settings.json").write_text(json.dumps({"artifacts": "artifacts"}), encoding="utf-8")
            env = dict(os.environ, VERIFY_SETTINGS=str(root / "settings.json"))
            result = subprocess.run(["node", str(VERIFY / "guard" / "drive.mjs"), "run-1", "snapshot"], cwd=tmp,
                                    capture_output=True, text=True, env=env)
            names = sorted(path.name for path in (run_folder / ".playwright-cli").iterdir())
            saved = (run_folder / ".playwright-cli" / "page-1.yml").read_text(encoding="utf-8")
            notes = (run_folder / "explore.md").read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(names, ["page-1.yml"])
        shown = result.stdout + result.stderr + saved
        for secret in ("fictional-123", "fictional-456", "fictional-frag6", "fictional-rel", "fictional-dot",
                       "fictional-bare", "fictional-frag", "fictional-paren", "fictional-md", "fictional-par",
                       "fictional-apos", "fictional-quoted"):
            self.assertNotIn(secret, shown, secret)
        self.assertIn("[Open](http://app.test/a) and (see http://app.test/b)", result.stdout)
        self.assertIn("Page URL: http://localhost:8101/accounts/o'neil/verify\n", result.stdout)
        self.assertIn("goto('http://app.test/c') done", result.stdout)
        self.assertIn("wss://app.test/socket", result.stderr)
        for line in ("- Page URL: http://[::1]:8101/labels", "  - /url: /callback\n", "  - /url: callback\n",
                     '- textbox "Search": ?name=Camembert', "- text: Keep /A#12 label"):
            self.assertIn(line, saved, line)
        self.assertEqual(notes, "Session: run-1-1-1\n")

    def test_the_runner_uses_the_skill_config_and_keeps_the_exit_code(self):
        result = self.runner("doctor.spec.ts")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("test --config", result.stdout)
        self.assertRegex(result.stdout, r"skill[\\/]playwright\.config\.ts doctor\.spec\.ts")
        self.assertRegex(result.stdout, r"skill [^\n]*[\\/]skill\n")
        self.assertIn("proxy none", result.stdout)
        self.assertIn("connect none", result.stdout)

    STUB_CLI = r"""
const fs = require('node:fs');
fs.mkdirSync('.playwright-cli', { recursive: true });
fs.writeFileSync('.playwright-cli/console-1.log', 'GET http://app.test/api/x?token=fictional-123 ok\n');
fs.writeFileSync('.playwright-cli/page-1.yml', [
  '- Page URL: http://[::1]:8101/labels#fictional-frag6',
  '- link [ref=e1]:',
  '  - /url: /callback?token=fictional-rel',
  '  - /url: ./next?code=fictional-dot',
  '  - /url: ?token=fictional-bare',
  '  - /url: callback#fictional-frag',
  '  - /url: /callback?token=(fictional-paren)',
  '- textbox "Search": ?name=Camembert',
  '- text: Keep /A#12 label',
  '',
].join('\n'));
console.log('[Open](http://app.test/a?token=fictional-md) and (see http://app.test/b?x=fictional-par)');
console.log("Page URL: http://localhost:8101/accounts/o'neil/verify?token=fictional-apos#fictional-apos-frag");
console.log("goto('http://app.test/c?token=fictional-quoted') done");
console.error('failed wss://app.test/socket?token=fictional-456');
process.exit(3);
"""
    STUB_TEST_CLI = r"""
console.log('args ' + process.argv.slice(2).join(' '));
console.log('skill ' + process.env.VERIFY_SKILL);
console.log('proxy ' + (process.env.HTTPS_PROXY ?? process.env.https_proxy ?? 'none'));
console.log('connect ' + (process.env.PW_TEST_CONNECT_WS_ENDPOINT ?? 'none'));
process.exit(1);
"""

def _node_runs_typescript() -> bool:
    import shutil
    import subprocess
    if not shutil.which("node"):
        return False
    version = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip().lstrip("v")
    return int(version.split(".")[0]) >= 23


@unittest.skipUnless(_node_runs_typescript(), "needs Node 23 or later to run TypeScript directly")
class SettingsBehaviour(unittest.TestCase):
    """Runs guard.ts loadSettings against a stand-in @playwright/test, without a browser."""

    BASE = {"devServer": "http://localhost:8101", "blockedHosts": ["app.example.com"], "loginFile": "login.env",
            "loginKeys": {"user": "U", "password": "P"}, "artifacts": "out"}

    def load(self, settings, local, run="t-1", script=None):
        import json
        import os
        import shutil
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stub = root / "node_modules" / "@playwright" / "test"
            stub.mkdir(parents=True)
            (stub / "package.json").write_text('{"name":"@playwright/test","type":"module","main":"index.js"}',
                                               encoding="utf-8")
            (stub / "index.js").write_text("export const test = { extend: () => ({}) }; export const expect = {};",
                                           encoding="utf-8")
            (root / "package.json").write_text('{"type":"module"}', encoding="utf-8")
            shutil.copy(VERIFY / "guard" / "guard.ts", root / "guard.ts")
            if local is not None:
                (root / "local.env").write_text(local, encoding="utf-8")
                settings = {**settings, "localFile": "local.env"}
            (root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            env = {**os.environ, "VERIFY_SETTINGS": "settings.json", "VERIFY_RUN": run}
            env.pop("TEST_WORKER_INDEX", None)
            entry = "guard.ts"
            if script is not None:
                (root / "probe.mjs").write_text(script, encoding="utf-8")
                entry = "probe.mjs"
            return subprocess.run(["node", "--no-warnings", entry], cwd=root, capture_output=True, text=True, env=env)

    REQUEST_PROBE = r"""
import { guardRequests } from './guard.ts';
const calls = [];
const api = {};
for (const method of ['fetch', 'get', 'post', 'put', 'patch', 'delete', 'head']) {
  api[method] = async (url, options) => { calls.push([method, String(url), options?.maxRedirects ?? null, options?.method ?? null, options?.headers?.['content-type'] ?? null, options?.data ? String(options.data) : null, options?.form ? JSON.stringify(options.form) : null]); return 'ok'; };
}
guardRequests(api);
await api.get('http://localhost:8000/api/x?id=1');
await api.post('https://api.example.com/api/y?z=1', { data: 'v' });
await api.get('/relative');
await api.fetch({ url: () => 'https://api.example.com/graphql', method: () => 'POST', headers: () => ({ 'content-type': 'application/json' }), postDataBuffer: () => Buffer.from('{"q":1}') });
const sent = calls.at(-1);
await api.fetch({ url: () => 'https://api.example.com/search', method: () => 'POST', headers: () => ({}), postDataBuffer: () => Buffer.from('old=1') }, { form: { q: 'new' } });
await api.fetch({ url: () => 'https://api.example.com/keep', method: () => 'POST', headers: () => ({}), postDataBuffer: () => Buffer.from('kept=1') }, { form: undefined });
let refused = '';
try { await api.get('https://elsewhere.example.org/z'); } catch (error) { refused = error.message; }
const down = {};
for (const method of ['fetch', 'get', 'post', 'put', 'patch', 'delete', 'head']) {
  down[method] = async () => { throw new Error('connect ECONNREFUSED'); };
}
guardRequests(down);
let passedOn = '';
try { await down.get('http://localhost:8000/api/state'); } catch (error) { passedOn = error.message; }
const { readFileSync } = await import('node:fs');
const networkLog = readFileSync('out/t-1/network.log', 'utf8');
console.log(JSON.stringify({ passedOn, failedLogged: networkLog.includes('failed REQUEST GET http://localhost:8000\n') }));
console.log(JSON.stringify({ calls, refused, sent }));
"""

    def test_requests_from_the_test_follow_the_same_origin_rules(self):
        import json
        settings = {**self.BASE, "rewrite": ["https://api.example.com"]}
        result = self.load(settings, "VERIFY_BACKEND=http://localhost:8000\n", script=self.REQUEST_PROBE)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.strip().splitlines()
        down = json.loads(lines[-2])
        self.assertEqual(down["passedOn"], "connect ECONNREFUSED")
        self.assertTrue(down["failedLogged"])
        report = json.loads(lines[-1])
        self.assertEqual(report["calls"], [
            ["get", "http://localhost:8000/api/x?id=1", 0, None, None, None, None],
            ["post", "http://localhost:8000/api/y?z=1", 0, None, None, "v", None],
            ["get", "http://localhost:8101/relative", 0, None, None, None, None],
            ["fetch", "http://localhost:8000/graphql", 0, "POST", "application/json", '{"q":1}', None],
            ["fetch", "http://localhost:8000/search", 0, "POST", None, None, '{"q":"new"}'],
            ["fetch", "http://localhost:8000/keep", 0, "POST", None, "kept=1", None],
        ])
        self.assertIn("is not an allowed origin", report["refused"])

    def test_run_names_of_shared_folders_are_refused(self):
        for name in ("worktrees", "journeys", "Worktrees", "worktrees.md"):
            result = self.load(self.BASE, "VERIFY_BACKEND=http://localhost:8000\n", run=name)
            self.assertNotEqual(result.returncode, 0, name)
            self.assertIn("is kept for the artifacts folder's shared", result.stderr, name)

    def test_an_empty_blocked_list_is_allowed_only_with_a_pin(self):
        empty = {**self.BASE, "blockedHosts": []}
        result = self.load(empty, "VERIFY_BACKEND=http://localhost:8000\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blockedHosts is empty", result.stderr)
        result = self.load(empty, "VERIFY_BACKEND=http://api.example.com\nVERIFY_PIN_BACKEND_TO=127.0.0.1\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_also_allow_takes_only_this_machine(self):
        result = self.load({**self.BASE, "alsoAllow": ["https://other-api.example"]}, "VERIFY_BACKEND=http://localhost:8000\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("alsoAllow takes only addresses on this machine", result.stderr)
        result = self.load({**self.BASE, "alsoAllow": ["http://127.0.0.1:9000"]}, "VERIFY_BACKEND=http://localhost:8000\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_named_backend_without_a_pin_is_refused(self):
        result = self.load(self.BASE, "VERIFY_BACKEND=http://remote.example\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is a name, not this machine", result.stderr)

    def test_a_production_backend_is_refused_even_with_a_trailing_dot(self):
        result = self.load(self.BASE, "VERIFY_BACKEND=https://app.example.com./\nVERIFY_PIN_BACKEND_TO=::1\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is a production host; refusing to start", result.stderr)

    def test_also_allow_cannot_name_a_blocked_host_with_a_trailing_dot(self):
        result = self.load({**self.BASE, "alsoAllow": ["https://app.example.com."]}, "VERIFY_BACKEND=http://localhost:8000\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("alsoAllow takes only addresses on this machine", result.stderr)

    def test_a_missing_local_file_is_refused(self):
        result = self.load({**self.BASE, "localFile": "nowhere.env"}, None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is missing; copy verify.local.example", result.stderr)

    def test_settings_without_a_local_file_are_refused(self):
        import json
        settings = {**self.BASE, "backend": "http://localhost:8000"}
        result = self.load(settings, None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("settings need a localFile", result.stderr)

    def test_rewrite_as_a_map_is_refused(self):
        result = self.load({**self.BASE, "rewrite": {"https://api.example.org": "http://localhost:8000"}},
                           "VERIFY_BACKEND=http://localhost:8000\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rewrite is a list of origins", result.stderr)

    def test_a_local_backend_loads(self):
        result = self.load(self.BASE, "VERIFY_BACKEND=http://localhost:8000\n")
        self.assertEqual(result.returncode, 0, result.stderr)
