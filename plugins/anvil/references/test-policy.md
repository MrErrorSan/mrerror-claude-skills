# Test policy

Each kind of test covers what the others miss. Saad approves the test list at the plan stop. The test list format is in [formats.md](formats.md).

## The four test types

| Type | What it is | When it runs |
|---|---|---|
| `smoke` | One per main user-facing path: the thing starts and the path works (a CLI call, curl, or a browser step). | After each merged wave, and on the final state. It is the behavior evidence for the converge check. Keep them few and short: tests that touch a live service are never reused. |
| `keep` | A behavior test at a core seam. It names its S-line and what breaks if it fails. | Targeted, per task, during the build. The full suite runs once at the end. |
| `repro` | A bug reproduction, written before the fix. This is the one place where test-first is cheapest. | Before the fix; it then becomes a keep test. |
| `scaffold` | A test used only during the build. | Deleted in finish, and the deletion is listed in the report. |

## Budget per kind of work

- Scaffolding, config or types: 1–2 smoke tests.
- A feature: 3–5 behavior tests per feature, plus its smoke path.
- A bug: a repro plus a regression guard.
- An enhancement: only the new or changed behavior.

Going over budget needs a reason written in the plan.

## Name the tests, not the method

The plan names the tests that guard each task. It does not say "do TDD". Naming the affected tests is what cuts regressions; a TDD instruction without them made results worse.

The plan also records the full-suite command and how long it takes.

## Running tests

- An implementer runs only its task's targeted tests (`anvil run --scope targeted -- <cmd>`), plus the type-check (`anvil run --scope check -- <cmd>`). It never runs the full suite.
- A reviewer never reruns tests.
- Before rerunning anything, check `anvil fresh --scope <the scope it ran with> -- <cmd>`: a passing result on the same tree is reused. Runs that used live services or the network (`--external`), and test runs that ran no tests, are never reused. A `check` run (type-check, lint, build) is reused on exit 0.
- The full suite runs once, on the final merged state. It also runs after each wave only when it takes under about 2 minutes.

## Test changed or code changed

For every test touched, the report says whether **the test changed** or **the code changed**, and which S-line allows it.

- Editing a test to make it pass needs a changed S-line, named in the commit or the progress entry.
- Without one, the code gets fixed, not the test.
- A hook warns when a `keep` test file is edited, as a reminder to make this statement.
