---
name: performance
uses: [tdd, code-review]
fallbacks: [Measurement-limited analysis]
approval-exceptions: none
---

# Performance

Make it measurably faster or lighter, and be sure the number means what it seems to.

1. **Name the workload and the metric:** what is slow, for whom, on which data and machine, and the target.
2. **Baseline.** Measure before touching anything, with the same workload you will measure after.
3. **Explain the number.** Find what limits it and rule out measuring something else (warm-up, caching, the harness itself).
4. **Isolate the cost** with a profile or a focused benchmark.
5. **Change in this order:** don't do it, do it once, do less, do it later, do it cheaper.
6. **Remeasure** the same workload; keep correctness tests green (`tdd`) and review with `code-review`.

No representative environment: record Measurement-limited analysis and label where the numbers came from.

**Done when:** before and after numbers on the same workload are recorded with how they were measured, and behaviour is unchanged.
