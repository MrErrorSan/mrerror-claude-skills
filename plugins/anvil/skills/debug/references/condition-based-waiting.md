<!-- adapted from superpowers@7.0.2: skills/systematic-debugging/condition-based-waiting.md, skills/systematic-debugging/condition-based-waiting-example.ts -->

# Condition-based waiting

Flaky tests often guess at timing with fixed delays. That creates race conditions: the test passes on a fast machine and fails under load or in CI.

Wait for the condition you actually care about, not for a guess at how long it takes.

## When to use it

- Tests have fixed delays (`setTimeout`, `sleep`, `time.sleep()`).
- Tests are flaky: they pass sometimes and fail under load.
- Tests time out when run in parallel.
- A test waits for an async operation to finish.

**Not when** the test is about timing itself (debounce, throttle intervals). Then a fixed delay is correct, with a comment saying why.

## Core pattern

```typescript
// Before: guessing at timing
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// After: waiting for the condition
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

## Quick patterns

| Scenario | Pattern |
|----------|---------|
| Wait for an event | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| Wait for a state | `waitFor(() => machine.state === 'ready')` |
| Wait for a count | `waitFor(() => items.length >= 5)` |
| Wait for a file | `waitFor(() => fs.existsSync(path))` |
| Complex condition | `waitFor(() => obj.ready && obj.value > 10)` |

## Implementation

A generic polling function:

```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const startTime = Date.now();

  while (true) {
    const result = condition();
    if (result) return result;

    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(r => setTimeout(r, 10)); // Poll every 10ms
  }
}
```

Domain helpers are thin wrappers over this: `waitForEvent(type)`, `waitForEventCount(type, n)` and `waitForEventMatch(predicate, description)` each pass a different condition, and put the count they got into the timeout message.

## Worked example

From the session that fixed 15 flaky tests: an agent runs two tools, the test aborts it, then checks the results.

```typescript
// Before (flaky):
const messagePromise = agent.sendMessage('Execute tools');
await new Promise(r => setTimeout(r, 300)); // hope the tools start in 300ms
agent.abort();
await messagePromise;
await new Promise(r => setTimeout(r, 50));  // hope the results arrive in 50ms
expect(toolResults.length).toBe(2);         // fails at random

// After (reliable):
const messagePromise = agent.sendMessage('Execute tools');
await waitForEventCount(threadManager, threadId, 'TOOL_CALL', 2);   // tools started
agent.abort();
await messagePromise;
await waitForEventCount(threadManager, threadId, 'TOOL_RESULT', 2); // results arrived
expect(toolResults.length).toBe(2);
```

## Common mistakes

- **Polling too fast** (`setTimeout(check, 1)`) wastes CPU. Poll every 10ms.
- **No timeout** loops forever if the condition is never met. Always set one, with a clear error.
- **Stale data:** reading state once before the loop. Call the getter inside the loop.

## When a fixed delay is correct

```typescript
// Tool ticks every 100ms - need 2 ticks to verify partial output
await waitForEvent(manager, 'TOOL_STARTED'); // First: wait for condition
await new Promise(r => setTimeout(r, 200));   // Then: wait for timed behavior
// 200ms = 2 ticks at 100ms intervals - documented and justified
```

It needs all three:

1. first wait for the triggering condition;
2. a delay based on known timing, not a guess;
3. a comment that says why.

## Result in that session

15 flaky tests fixed across 3 files, the pass rate went from 60% to 100%, and the run got 40% faster.
