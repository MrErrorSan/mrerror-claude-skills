<!-- adapted from superpowers@7.0.2: skills/systematic-debugging/defense-in-depth.md -->

# Defense in depth

When you fix a bug caused by invalid data, one validation check feels like enough. But another code path, a later refactor or a mock can go around that one check.

So validate at each layer the data passes through, and make the bug structurally impossible rather than fixed once.

## Why several layers

One check says "we fixed the bug". Several say "this bug can't happen". Different layers catch different cases:

- entry validation catches most bugs;
- business-logic checks catch edge cases;
- environment guards stop dangers specific to a context (tests, CI);
- debug logging helps when the other layers fail.

Match the depth to the bug. A wrong path that ran `git init` in the source tree earns four layers; an off-by-one in a formatter earns its fix and its repro test.

## The four layers

### Layer 1: entry point validation

Reject obviously invalid input at the API boundary.

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
  // ... proceed
}
```

### Layer 2: business logic validation

Check that the data makes sense for this operation.

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace initialization');
  }
  // ... proceed
}
```

### Layer 3: environment guards

Refuse dangerous operations in specific contexts.

```typescript
async function gitInit(directory: string) {
  // In tests, refuse git init outside temp directories
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));

    if (!normalized.startsWith(tmpDir)) {
      throw new Error(
        `Refusing git init outside temp dir during tests: ${directory}`
      );
    }
  }
  // ... proceed
}
```

### Layer 4: debug instrumentation

Capture context for later investigation.

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('About to git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
  // ... proceed
}
```

## Applying the pattern

1. **Trace the data flow:** where does the bad value start, and where is it used?
2. **Map the checkpoints:** list each point the data passes through.
3. **Add validation at each layer:** entry, business logic, environment, debug.
4. **Test each layer:** get past layer 1 on purpose and check that layer 2 catches it.

## Example

Bug: an empty `projectDir` caused `git init` in the source code.

**Data flow:**

1. Test setup → empty string.
2. `Project.create(name, '')`.
3. `WorkspaceManager.createWorkspace('')`.
4. `git init` runs in `process.cwd()`.

**Four layers added:**

- Layer 1: `Project.create()` checks the directory is not empty, exists and is writable.
- Layer 2: `WorkspaceManager` checks projectDir is not empty.
- Layer 3: `WorktreeManager` refuses `git init` outside the temp dir in tests.
- Layer 4: a stack trace is logged before `git init`.

**Result:** all 1847 tests passed, and the bug could no longer be reproduced.

## What that session showed

Each of the four layers caught something the others missed:

- other code paths went around the entry validation;
- mocks went around the business-logic checks;
- edge cases on other platforms needed the environment guard;
- the debug logging exposed structural misuse.

One validation point is rarely enough for a bug like this.
