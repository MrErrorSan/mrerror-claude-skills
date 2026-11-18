<!-- adapted from superpowers@7.0.2: skills/systematic-debugging/root-cause-tracing.md -->

# Root cause tracing

Bugs often show up deep in the call stack: `git init` in the wrong directory, a file created in the wrong place, a database opened with the wrong path. The natural move is to fix the line where the error appears, but that treats the symptom.

Trace backward through the call chain until you find the original trigger, then fix it at the source.

## When to use it

- The error happens deep in execution, not at the entry point.
- The stack trace shows a long call chain.
- It's unclear where the invalid data came from.
- You need to find which test or which code path triggers the problem.

If the trail really does dead-end (you can't go up another level), fix at the point you reached and say that it is a symptom fix. Once you've found the source, also consider [defense-in-depth.md](defense-in-depth.md).

## The tracing process

### 1. Observe the symptom

```
Error: git init failed in ~/project/packages/core
```

### 2. Find the immediate cause

What code directly causes this?

```typescript
await execFileAsync('git', ['init'], { cwd: projectDir });
```

### 3. Ask what called it

```typescript
WorktreeManager.createSessionWorktree(projectDir, sessionId)
  → called by Session.initializeWorkspace()
  → called by Session.create()
  → called by test at Project.create()
```

### 4. Keep tracing up

What value was passed?

- `projectDir = ''` (an empty string).
- An empty string as `cwd` resolves to `process.cwd()`.
- That is the source code directory.

### 5. Find the original trigger

Where did the empty string come from?

```typescript
const context = setupCoreTest(); // Returns { tempDir: '' }
Project.create('name', context.tempDir); // Accessed before beforeEach!
```

## Adding stack traces

When you can't trace by reading, instrument the code just before the problem operation:

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  console.error('DEBUG git init:', {
    directory,
    cwd: process.cwd(),
    nodeEnv: process.env.NODE_ENV,
    stack,
  });

  await execFileAsync('git', ['init'], { cwd: directory });
}
```

In tests, use `console.error()` rather than the app's logger, which may be suppressed. Run and capture:

```bash
npm test 2>&1 | grep 'DEBUG git init'
```

Then read the stack traces: look for test file names, find the line that triggers the call, and look for a pattern (the same test, the same parameter).

## Finding which test causes pollution

If something appears during the test run and you don't know which test creates it, use the bisection script `scripts/find-polluter.sh` that ships with this skill (SKILL.md gives the full command):

```bash
bash <skill dir>/scripts/find-polluter.sh '.git' 'src/**/*.test.ts'
```

It runs the test files one at a time with `npm test <file>` and stops at the first one that creates the path. For another test runner, change that one line in a copy.

## Real example: empty projectDir

**Symptom:** `.git` created in `packages/core/` (the source code).

**Trace chain:**

1. `git init` runs in `process.cwd()`, because the `cwd` parameter is empty.
2. WorktreeManager was called with an empty projectDir.
3. `Session.create()` passed an empty string.
4. The test read `context.tempDir` before `beforeEach` ran.
5. `setupCoreTest()` returns `{ tempDir: '' }` at first.

**Root cause:** a top-level variable initialisation read a value before it was set.

**Fix:** `tempDir` became a getter that throws if it is read before `beforeEach`.

**Defense in depth, added afterwards:**

- Layer 1: `Project.create()` validates the directory.
- Layer 2: WorkspaceManager checks it isn't empty.
- Layer 3: a `NODE_ENV` guard refuses `git init` outside the temp dir.
- Layer 4: a stack trace is logged before `git init`.

## The principle

Found the immediate cause → can you trace one level up? If yes, trace back and ask whether this is the source; repeat until it is. Fix at the source, then add validation at each layer. Fixing only where the error appears leaves every other path to the same bug open.

## Stack trace tips

- **In tests:** use `console.error()`, not the logger; the logger may be suppressed.
- **Before the operation:** log before the dangerous operation, not after it fails.
- **Include context:** directory, cwd, environment variables, timestamps.
- **Capture the stack:** `new Error().stack` shows the complete call chain.

## Result in that session

A five-level trace found the root cause, the fix went in at the source (getter validation), four layers of defense were added, and all 1847 tests passed with no pollution.
