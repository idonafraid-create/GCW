# QA scenarios

Use fixed conditions for source and candidate: viewport, DPR, browser/backend, theme, route, crop, readiness, pointer, scroll, random seed and time phase. Put these values in the capture scenario JSON rather than relying on operator memory.

Minimum matrix:

| Surface | Required scenarios |
|---|---|
| Homepage | ready initial frame, later frame, pointer left/center/right |
| Scroll | top, early transition, target animated section, footer |
| Responsive | canonical desktop and mobile viewport |
| Navigation | mobile menu, one internal transition, direct deep link |
| Routes | every recovered public route opens; representative content/title assertions |
| GPU | one valid owner surface after loading; no shader link failure |
| Build | clean install when practical, production build, static preview |

For random or compositor-driven effects, inject the same deterministic RNG when safe, freeze the JavaScript clock only after both pages are ready, and record remaining compositor-sensitive regions separately. Never use an entry/loading overlay as a target frame; wait for an observable readiness condition such as the final canvas count or visible shell state.

## Threshold guidance

- Treat numeric thresholds as project-specific gates, not universal definitions of quality.
- A large deterministic change in a primary surface is P1/P2 even if the global changed-pixel percentage looks small.
- A high footer diff caused by independently advancing particles may be phase-sensitive rather than a layout failure.
- Always inspect the generated diff image before accepting a metric.
