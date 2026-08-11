# Round 5, STATUS: SA-v2 rerun complete — interaction REVERSED, adjudicated final

Last updated 2026-08-11. **Read this before citing any round-5 number.**

## 2026-08-11 addendum: the 9 similarity flags are ruled

The owner ruled all 9 gold-overlap flags honest convergence (evidence:
detection grep 0/60, no retrieval language in any meta, no fix-SHA in
the branch tree, provenance-clean state file, 4 of 9 flagged instances
failed grading, requirement texts enumerate the change file-by-file;
full packet in the source repo). The v2 numbers below are final. The
cwd-trap handicap caveat still applies to the magnitude, not the sign.

## 2026-08-05 addendum: the SA rerun is complete and analyzed

The pre-registered rerun (sanitized `tasks_v2/` with instance_id withheld,
explicit provenance rule in `protocol_armA_v2.md`, fresh state file, branch
`bench5/armA-sonnet5-v2`) delivered 60/60 and graded with the official
harness, all 60 genuine:

- **SA-v2: 29/60 (48.3%)** vs SB 48/60 — sonnet scaffolding effect
  **−31.7pp**, McNemar 4-vs-23, exact **p = 0.0003** (negative).
- Opus effect unchanged: +11.7pp, p = 0.0391.
- **Interaction (ΔS−ΔO): −43.3pp, bootstrap 95% CI [−61.7, −25.0]** —
  significant, sign OPPOSITE the pre-registered H1. Low-probe subset agrees
  (interaction −47.6pp, CI excludes 0).
- Reading: with the answer key removed, fresh-session scaffolding HELPED the
  frontier model and HURT the smaller one on this stratum; the original SA
  "+16.7pp scaffolding gain" was answer-key retrieval.

Two caveats before publishing hard numbers (details in `RUN.md`
§ 2026-08-05): (1) a sandbox cwd/hook trap handicapped ~13 of the 60
deliveries (hand-built diffs, unverifiable in-session) — the clean-delivery
subset still runs ~25pp below SB, so the sign is robust but the magnitude is
inflated by some share; (2) 9 gold-overlap similarity flags (no retrieval
language in any meta; 4 of 9 failed grading) — ruled honest convergence
by the owner, 2026-08-11 (see the addendum at the top of this file).
Audit otherwise clean: detection grep 0/60, fix-SHA sweep of the branch
zero, carried state file provenance-clean, graded-vs-final byte check clean.

Use `results/main_matrix_v2.json` for anything involving sonnet-scaffolded;
`results/main_matrix.json` remains authoritative ONLY for OA/SB/OB and the
historical record of the disqualified SA row.

## 2026-08-04 addendum: the open decisions below are ruled

1. **The exploit is a reported finding.** It leads the top-level README.
2. **SA reruns.** The rerun withholds instance IDs from the agent entirely (the
   rank-to-ID mapping stays with the orchestrator) and is pre-registered as an
   amendment in the source repo before launch. The interaction publishes when
   it grades.

SA's original pass rate stays excluded from every analysis. It appears in the
README only inside the disqualification table. The review below is preserved
as written on 2026-08-03.

## Where the truth lives

This directory is a **mirror**. The authoritative copy is the `agentic-sdlc`
repo, branch `bench5/base`, directory `bench5/`. When the two disagree, that
one wins. `TELEMETRY.md` (synced here) is the full catalogue of what lives where.

| File | Use it? |
|---|---|
| `results/main_matrix.json` | **Yes — authoritative.** The 60x4 pass matrix, pre-registered analyses, high-probe list. |
| `results/main_armB_grades.json` | Yes. All 120 arm-B grades. |
| `results/main_armA_grades.PARTIAL-DO-NOT-USE.json` | **No.** The grader emits only *newly graded* entries, so this holds 9 of 60 per cell. Computing a pass rate from it gives a wrong answer — it is kept only for provenance. Use `main_matrix.json`. |
| `RUN.md`, `PLAN.md`, `TELEMETRY.md` | Yes, synced 2026-08-03. |

## Run state

All four cells ran 60/60 and all 240 patches were graded with the official
SWE-bench Pro harness. Cron triggers disabled. Nothing is still executing.

## The headline is not safe to publish yet

A review on 2026-08-03 found that **arm A / sonnet-5 (cell SA) solved a large
share of its instances by retrieving the real upstream fix**, not by doing the
engineering task.

`instance_id` embeds the gold fix commit SHA. SA discovered this, wrote it into
its carried state file — which *is* the scaffolding treatment — and reused it for
the rest of the run. Its own state file says so: *"`instance_id` often embeds the
exact upstream fix commit hash (35/35 so far)"*, followed by a worked recipe for
`git diff base_commit <hash>` / `cherry-pick -n`, including retrieving the
held-out `test_patch` to self-grade and deleting it again before the final diff.

**45 of 60 SA meta files** explicitly describe cherry-picking or diffing against
the upstream fix commit.

Cell-by-cell exposure:

| Cell | Metas referencing the upstream fix | Verdict |
|---|---|---|
| SA (sonnet, scaffolded) | **45 / 60** | **Pass rate invalid** |
| OA (opus, scaffolded) | 0 / 60 | Clean |
| SB (sonnet, bare) | 0 / 60 | Clean |
| OB (opus, bare) | 0 / 60 | Clean |

The three loose keyword hits in OA are false positives — all describe moving code
that already existed inside the repo. OA's carried state file contains the
opposite instruction, in its own words: **"Never fetch the fix commit."**

### What this does to each pre-registered claim

- **Opus scaffolding effect (OA vs OB): stands.** +11.7pp, McNemar 8-vs-1,
  exact p = 0.0391, on a stratum where the bare arm scored 86.7%. Both cells clean.
- **Sonnet scaffolding effect (SA vs SB): withdrawn.** SA's 58/60 is not a
  measurement of scaffolded engineering.
- **H1, the interaction: not computable.** It needs a valid ΔSonnet.
- **Low-probe sensitivity subset: inherits the same problem** for its SA column.

### Open decisions for the owner

1. Whether to re-run SA with `instance_id` withheld or the fix commit blocked at
   the network layer, which would restore H1.
2. Whether the exploit becomes its own reported finding. It is a real one: under an
   identical protocol on an identical battery, the frontier model wrote
   *"never fetch the fix commit"* into its memory and the smaller model
   industrialised the shortcut instead.
3. H5 (cost) is still unresolved — per-cell token totals were never captured; see
   `RUN.md` § 2026-08-03.

Until 1 and 2 are ruled on, **do not publish SA's pass rate, the interaction, or
any "scaffolding helps the weaker model more" framing.**
*(Ruled on 2026-08-04; see the addendum at the top of this file.)*
