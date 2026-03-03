# heliosCLI Absorb + Archive Readiness Package (2026-03-03)

## Canonical Target
`heliosCLI` is the canonical target for absorb/migration.

Rationale summary:
- `heliosCLI` carries active integration branch work and tracked upstream lineage (`upstream/main` present and current in branch graph).
- `helios-cli` is currently a divergent mirror with `main` ahead/behind drift and additional local artifact noise.

## Captured Heads
See `.archive/absorb-readiness-2026-03-03/repo-heads.env` for exact branch + SHA captures.

## Delta Manifests
Tracked-file-only manifests captured pre-normalization:
- `.archive/absorb-readiness-2026-03-03/heliosCLI.tracked-delta.manifest.txt`
- `.archive/absorb-readiness-2026-03-03/helios-cli.tracked-delta.manifest.txt`

These exclude common artifact/build paths:
- `dist/**`
- `build/**`
- `target/**`
- `.cache/**`

## Worktree Normalization
Safe non-destructive normalization performed:
- `heliosCLI`: committed current dirty state to `chore/normalize-dirty-20260303-heliosCLI`.
- `helios-cli`: committed current dirty state to `chore/normalize-dirty-20260303-helios-cli`, intentionally excluding large untracked artifact directory `repos/`.

Post-normalization status snapshots are archived in:
- `.archive/absorb-readiness-2026-03-03/heliosCLI.post-normalize.status.txt`
- `.archive/absorb-readiness-2026-03-03/helios-cli.post-normalize.status.txt`

## Migration Checklist
See:
- `docs/checklists/HELIOSCLI_MIGRATION_CHECKLIST_2026-03-03.md`
