# Bounded work and failure recovery

**Applies to:** services, jobs, queues, network operations, caches and retrying work. These are review requirements when relevant, not an instruction to add a distributed-systems framework.

## Required

- Establish which failures can be retried and which operations are safe to repeat. A timeout does not prove a remote side effect never happened. Preserve established deduplication/transaction identities; do not invent keys with no server-side guarantee.
- Bound retries and concurrency. Define the deadline/budget and stopping conditions, honour cancellation, and avoid multiplying retries independently at several layers.
- Keep work accumulation bounded or justify the required retention. Review queue size, cache growth, resource use, batch size and output accumulation; choose limits based on the workload, not arbitrary global numbers.
- Make degraded or failed operation visible through the appropriate user result and safe diagnostics. Do not hide a failure with a success-shaped default or repeat it indefinitely.
- Identify the consistency boundary for state changes. A database transaction does not automatically make external effects such as messages or payments atomic. Handle ordering/reconciliation using established project mechanisms.

## Defaults and example

Reuse the project's retry/backoff and queue policy. Where needed, stagger retries rather than synchronising every client, but do not retry validation or permission failures indiscriminately.

A queued operation may run again after the first result was lost. Its durable effect should follow the agreed repeat-delivery contract, rather than merely rely on an in-memory boolean. Ask about that contract when the owner has not decided it.

## Verification

Test the consequential cases: transient failure, exhausted budget, cancellation, duplicate delivery, partial completion and recovery. Check that retrying does not duplicate side effects or amplify failures. Use local controlled fixtures; testing never authorises real purchases, production jobs or destructive operations.

Sources: [Amazon retry/timeout guidance](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/), [Laravel queue transactions/retries](https://laravel.com/docs/12.x/queues). The Laravel link illustrates a versioned implementation; use the matching version for actual work.
