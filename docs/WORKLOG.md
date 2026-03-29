# Worklog

Active work tracking for **heliosCLI**.

---

## Current Lanes

| Lane | Branch | Worktree | Status | Notes |
| --- | --- | --- | --- | --- |
| Rollout limit safety fix | `fix/rollout-limit-expect` | `/Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI` | Draft PR open | PR [#130](https://github.com/KooshaPari/heliosCLI/pull/130), base `main` |
| Codex core parked work | `wip/codex-rs-core` | `/Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI-wtrees/codex-rs-core` | Active | Parked WIP lane, not merged |
| CI failures lane | `fix/ci-failures` | `/Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI-wtrees/fix-ci-failures` | Active | Side lane in progress |
| Key router decomposition | `refactor/decompose-key-router` | `/Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI/heliosCLI-wtrees/decompose-key-router` | Active | Refactor lane in progress |

---

## Merged Baseline on `main`

Recent merged commits already on `origin/main`:

1. `#126` Deprecated criterion cleanup
2. `#128` kitty-specs to docs/specs migration
3. `#125` rust-ci/codespell/cargo-deny fixes
4. `#127` Additional deprecated criterion cleanup
5. `#124` KeyEventRouter extraction refactor

---

## Remaining Work

1. Resolve and merge draft PR `#130` (`fix/rollout-limit-expect`).
2. Decide disposition of `wip/codex-rs-core`: split into reviewable PRs or continue as parked WIP.
3. Finish or close `fix/ci-failures` and `refactor/decompose-key-router` lanes.
4. Reconcile current root worktree drift (`package.json` modified) with the intended lane before further merges.

---

_Last updated: 2026-03-28_
