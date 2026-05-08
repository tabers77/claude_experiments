# Self-Learning System — Audit

**Date**: 2026-05-08
**Scope**: the self-learning skill machinery built across `library/templates/self-learning-skill/`, the four standardized phases (audit, ledger, mid-run capture, observer), the seven capture channels, and the two retrofitted reference skills (`pr-merge-readiness`, `shared-bug-gap-fix`).
**Out of scope**: cross-skill audits across the wider plugin (use `/meta-skill-audit` for that), domain-phase quality of any specific skill.

## Headline verdict

The system is **structurally sound and ready to test**, with **3 weaknesses worth addressing before scale**:

1. **Boundary callout has no mechanical enforcement.** Domain phases reading `observations.json` is documented as forbidden but no FAIL tag catches it. The user spotted the leak only by chance. (HIGH)
2. **`_theme_slug` is an undocumented schema extension** — present in real `observations.json` files I wrote, not in `observations_schema_v1.md`. Drift risk. (HIGH)
3. **`friction_log[]` has two writers** (skill domain phases + observer narrow exception) without an explicit ownership doc. Risk of double-writes or contradictory entries. (MEDIUM)

Everything else is healthy. The audit pattern is proven (`shared-bug-gap-fix` has 3 auto-applied remediations on real runs). The observer is the new prototype piece; its complexity is justified by its purpose, but it is the largest single phase and worth keeping under observation as the prototype runs.

---

## System inventory

### Templates (7 files in `library/templates/self-learning-skill/`)

| File | Purpose | Required for self-learning skill? |
|---|---|---|
| `SKILL.md.tpl` | Frame for greenfield skill | ✅ mandatory |
| `audit-phase.md` | Phase N-1 body | ✅ mandatory |
| `ledger-phase.md` | Phase N body | ✅ mandatory |
| `run_history_schema_v1.md` | `run_history.json` schema + bootstrap | ✅ mandatory |
| `suggestion-capture.md` | Mid-run user-suggestion block | ⚠️ optional, default-on |
| `observer-phase.md` | Phase N+1 body + boundary callout | ⚠️ optional, default-off (prototype) |
| `observations_schema_v1.md` | `observations.json` schema + `suggestions.md` format | conditional on observer |

### Phases (4 standardized + N domain)

| Phase | Owner | Reads | Writes | Auto-apply? | Suggestion? |
|---|---|---|---|---|---|
| 1..N-2 | skill author | skill-specific | skill-specific | n/a | n/a |
| N-1 (audit) | template | run_history.json | nothing during audit; ledger writes after | n/a | yes (final-call) |
| N (ledger) | template | run_history.json | run_history.json (+ SKILL.md when threshold trips) | ✅ Mode B | persists captured |
| N+1 (observer) | template | run_history.json + observations.json | observations.json + suggestions.md (+ friction_log narrow exception) | ❌ never | n/a |

### Capture channels (7)

| # | Channel | File location | Writer | Lifecycle | Auto-apply | Rollback |
|---|---|---|---|---|---|---|
| 1 | `fail_counters[]` | `run_history.json` | audit phase increments; ledger persists | accumulates per run, resets on remediation | ✅ Mode B at threshold | `git revert` |
| 2 | `runs[]` | `run_history.json` | ledger phase | append-only | n/a | n/a (history) |
| 3 | `friction_log[]` | `run_history.json` | domain phases (original); observer (narrow exception for `dev_env_friction`) | append-only; manual `resolved_at` | ❌ never | manual edit |
| 4 | `improvement_suggestions[]` | `run_history.json` | mid-run capture protocol; audit final-call | append-only; manual `applied_at` | ❌ Tier 1 only (Tier 2/3 deferred) | manual edit |
| 5 | `observations[]` | `observations.json` | observer phase | append-only; user housekeeping deletion permitted | ❌ never | manual edit |
| 6 | `review_log[]` | `observations.json` | observer phase (clustering trips) | append-only; manual `applied_at` | ❌ never | manual edit |
| 7 | `suggestions.md` | freeform markdown | observer (append); user (status flips) | observer appends, human reviews | ❌ never | edit / delete sections |

### Rules (sub-mechanisms)

- **FAIL counter threshold tiers**: load-bearing=1, procedural=2, cosmetic=5 (audit channel only).
- **Cluster threshold**: default 3 (observer channel only).
- **Convergence rule**: observer count ≥1 + matching `improvement_suggestions[]` entry → trip regardless of cluster threshold.
- **Theme-similarity check**: within a tripped category, group observations by sub-theme; only sub-clusters at threshold trigger proposals.
- **Friction-log narrow exception**: observer MAY write to `friction_log[]` when category is `dev_env_friction`.
- **Boundary callout**: domain phases MUST NOT read `observations.json` or `suggestions.md`. Documented, not mechanically enforced.
- **Verbatim-quote rule**: audit rows AND observer evidence MUST quote user input verbatim. Audit has a FAIL tag for violation (`audit-paraphrased-user-input`); observer does not.

---

## Phase-by-phase strength evaluation

### Audit phase (Phase N-1) — STRONG

| Criterion | Status | Evidence |
|---|---|---|
| Clear trigger | ✅ | Fires immediately before terminal action |
| Clear exit condition | ✅ | Approval token (literal) — silence/"ok"/"looks good" do NOT advance |
| Evidence shape | ✅ | One row per domain phase, verbatim-quote slot for input-consuming phases |
| Failure modes covered | ✅ | 3 universal seed FAIL rules + N domain rules |
| Auto-apply safety | ✅ | Mode B with git diff as safety net |
| Real-world track record | ✅ | 3 auto-applied remediations on `shared-bug-gap-fix` |

**No weaknesses identified.** This is the most battle-tested phase.

### Ledger phase (Phase N) — STRONG

| Criterion | Status | Evidence |
|---|---|---|
| Clear trigger | ✅ | Last phase in domain+audit pipeline |
| Clear exit condition | ✅ | File written, threshold check completes |
| Evidence shape | ✅ | Append `runs[]`, increment `fail_counters[]`, persist `improvement_suggestions[]` |
| Failure modes covered | ✅ | Tolerates manual edits; refuses to write unrecognized schema versions |
| Real-world track record | ✅ | Multiple closed runs across both reference skills |

**Minor observation**: when the suggestion-capture block is opt-out, the ledger has conditional steps (skip "persist captured suggestions"). This is documented but adds branching complexity to the template.

### Observer phase (Phase N+1) — COHERENT BUT COMPLEX

| Criterion | Status | Evidence |
|---|---|---|
| Clear trigger | ✅ | After ledger writes |
| Clear exit condition | ⚠️ partial | Closes when observations + clustering complete; "no observations is valid" is explicit |
| Evidence shape | ✅ | Schema-defined `observations[]` row, verbatim-quote requirement |
| Failure modes covered | ⚠️ | NO FAIL tags exist for observer itself (boundary violation, theme-merge errors) |
| Real-world track record | ❌ | Zero live runs to date; only seeded-bootstrap state in both reference skills |

**Weaknesses identified:**

1. **Highest single-phase complexity in the system.** 8 steps + 3 cross-cutting rules (cluster threshold, convergence, theme-similarity) + narrow `friction_log` exception + boundary callout. By comparison, audit has 5 steps and ledger has 7.
2. **No FAIL tags policing the observer itself.** Audit has `audit-paraphrased-user-input` etc. that police the audit. Observer's own honesty rules ("never paraphrase", "never invent observations") are documented but not mechanically tracked. If observer drifts, no counter trips.
3. **Boundary callout enforcement is documentation-only.** The user already spotted one leak. There is no mechanical detection for "domain phase referenced observer-file content".

**Recommendation**: extend the universal seed FAIL set with at least one observer-honesty rule (`observer-paraphrased-user-input`, mirroring the audit's rule). Add `boundary_violation` to observer's standard category table so post-run leaks land in `observations.json` even though they can't be mechanically detected during the leak itself.

### Mid-run capture protocol — STRONG

| Criterion | Status | Evidence |
|---|---|---|
| Clear trigger | ✅ | 5 specific prefixes; anything else is normal conversation |
| Clear exit condition | ✅ | Record + acknowledge + resume current phase |
| Evidence shape | ✅ | Verbatim, structured into `improvement_suggestions[]` |
| Failure modes covered | n/a | No execution loop, just a recognizer |
| Real-world track record | ✅ | 2 captured suggestions on `pr-merge-readiness` |

**No weaknesses identified.** Tight, single-purpose, deterministic.

### Domain phases — variable per skill (out of scope for this audit)

The audit + ledger pattern doesn't constrain domain-phase quality directly. Each generated skill must self-validate via the "Self-learning checklist" at SKILL.md tail.

---

## Overlap analysis

### Capture-channel pairs (full matrix)

| Channel A | Channel B | Overlap? | Resolution |
|---|---|---|---|
| `fail_counters[]` | `friction_log[]` | ❌ none | mechanical FAIL vs. environmental pain — different writers, different lifecycles |
| `fail_counters[]` | `improvement_suggestions[]` | ❌ none | what went wrong (mechanical) vs. what could be better (user-perceived) |
| `fail_counters[]` | `observations[]` | ❌ none | mechanical detection vs. qualitative scan |
| `friction_log[]` | `improvement_suggestions[]` | ❌ none | environmental vs. SKILL.md-fixable |
| `friction_log[]` | `observations[]` | ⚠️ **partial** | observer's narrow exception lets it write `friction_log` for `dev_env_friction`. Two writers (skill + observer) for the same array. |
| `improvement_suggestions[]` | `observations[]` | ⚠️ intentional convergence | explicitly used by convergence rule. Both can record the same theme; that's the *point*, not a bug. |
| `improvement_suggestions[]` | `suggestions.md` | ❌ none | user-typed individual entries vs. observer-clustered proposal documents |
| `observations[]` | `suggestions.md` | ❌ none | observations are inputs; suggestions.md is downstream output |
| `runs[]` | `observations[]` | ⚠️ partial | observer's `run_ref` field cross-references `runs[].ts`. Intentional; not redundant. |

**Worst overlap**: `friction_log[]` dual-writer ambiguity. The original schema doc says friction entries are written "in the originating domain phase where the friction was experienced". The observer's narrow exception lets it ALSO write. The two writers are not coordinated. Risk: double-write of the same friction (skill phase records it, observer's post-run scan extracts it again from notes). No deduplication mechanism exists.

**Recommendation**: explicitly document in `run_history_schema_v1.md` that `friction_log` has two writers and how they coordinate (e.g., observer SHOULD scan `friction_log[]` for an entry with the same `target` + `phase` + similar `detail` and skip if a near-duplicate exists).

### Phase-pair overlap

| Phase A | Phase B | Overlap? |
|---|---|---|
| Audit (N-1) | Observer (N+1) | none — categorical/mechanical vs. qualitative/cross-run, file isolation enforced |
| Audit final-call | Mid-run capture | none — same `improvement_suggestions[]` array, but sequential not concurrent (capture during phases 1..N-2; final-call at end of audit) |
| Ledger (N) | Observer (N+1) | partial — both run "post-business-logic". Sequential and well-separated, but observer sees ledger's just-written state. Intentional. |
| Phase 7.5 user-resolution gate | Audit final-call | none — different purposes (resolve unresolved items vs. invite final suggestions) |

**No problematic phase overlaps.**

---

## Strengths (what's working well)

1. **Asymmetric auto-apply is justified.** Audit auto-applies (mechanical confidence is high); observer never auto-applies (qualitative confidence is lower). Asymmetry is by design and well-documented.
2. **Tagged-not-freeform invariant is consistent.** Both `fail_counters[]` and observer's category slugs use stable-forever tags. No freeform reflection drift.
3. **Verbatim-quote rule is consistently enforced.** Same rule across audit rows and observer evidence — audit has FAIL detection; observer doesn't but documents the rule clearly.
4. **Per-skill local ledger isolation.** Each skill is its own RL agent. No central state to corrupt; lessons don't propagate across skills (intentional).
5. **Boundary callout placement is correct (top of file, not buried at the bottom).** This is a structural design decision the templates make explicit — Claude reads top-to-bottom, so the prohibition has to land before any domain phase fires.
6. **Convergence rule is conservative the right way.** It overrides cluster threshold *upward* (lower count to trip a proposal when two channels agree), not *downward*. Two independent channels agreeing is genuinely stronger evidence than three same-channel hits.
7. **Schema versioning policy is safe.** "Skills must refuse to write a file whose version they don't recognize" pushes migration to the human, not silent coercion.
8. **Mid-run capture is in Tier 1 (capture-only) for now.** Tier 2 (manual aggregation) and Tier 3 (auto-apply) deferred until the data justifies them. Right call — premature aggregation would create noise.
9. **Friction-log narrow exception is well-bounded.** Observer can ONLY write to `friction_log[]`, ONLY for `dev_env_friction`. Hard limit prevents observer from creeping into general `run_history.json` writes.

---

## Weaknesses (prioritized)

### HIGH — Boundary callout has no mechanical enforcement
**Symptom**: domain phases can read `observations.json` and bias their behavior. Documented prohibition is the only safeguard. The user spotted one occurrence by chance.
**Fix**: add `boundary_violation` to observer's standard category table (post-run capture). For mechanical detection mid-run, would need per-phase file-read tracking — not currently possible without harness instrumentation.
**Cost**: 4 files, ~30 LOC.

### HIGH — `_theme_slug` is an undocumented schema extension
**Symptom**: `_theme_slug` field appears in real `observations.json` seed entries (in both `pr-merge-readiness` and `shared-bug-gap-fix`) but is NOT in `observations_schema_v1.md`. The schema's "tolerate any valid v1 JSON" rule allows it, but readers parsing the schema doc won't know it exists.
**Fix**: formalize `_theme_slug` in the schema as an OPTIONAL field used by the theme-similarity check. Document its purpose and naming convention.
**Cost**: 1 file (`observations_schema_v1.md`), ~15 LOC.

### MEDIUM — `friction_log[]` has two uncoordinated writers
**Symptom**: skill domain phases can write `friction_log` entries directly; observer can also write (narrow exception). No deduplication. Risk: same friction recorded twice.
**Fix**: document in `run_history_schema_v1.md` that observer SHOULD check for near-duplicate entries before writing. Add a "deduplication contract" sub-section.
**Cost**: 1 file (`run_history_schema_v1.md`), ~10 LOC.

### MEDIUM — Observer phase has no honesty FAIL tags
**Symptom**: audit polices itself via `audit-paraphrased-user-input` etc. Observer documents the same rule but has no counter, no mechanical detection. Observer drift would be invisible until a human notices.
**Fix**: add `observer-paraphrased-user-input` (load-bearing, threshold=1) to the universal seed FAIL set when observer is enabled. Audit-row check at next run scans observations recorded since last run for paraphrase markers.
**Cost**: 1 file (`run_history_schema_v1.md`) + observer phase update + audit-phase template update, ~25 LOC. Detection mechanism is fuzzier than audit's because evidence is observer-extracted, not user-spoken — partial detection only.

### LOW — Documentation drift risk
**Symptom**: 7 template/doc files with overlapping content (e.g., the observer file boundary callout appears in 4 places: template + 2 SKILL.md files + the design doc). Future edits will drift.
**Fix**: make `observer-phase.md`'s "Companion: Observer file boundary callout" the single source of truth; SKILL.md files should reference it rather than copy. (Trade-off: copying is what the inlining pattern requires; reference would break the "skill is self-contained" principle. Probably accept the duplication and add a top-of-file "edit-here-and-mirror" comment to each copy.)
**Cost**: minimal, comment additions only.

### LOW — Tier 2/3 promotion path for `improvement_suggestions[]` is undefined
**Symptom**: observer's convergence rule already references `improvement_suggestions[]`. If the user accumulates 10+ entries with similar `tag` values, no automated proposal path exists. Tier 1 (capture-only) is the current state by design.
**Fix**: design Tier 2 (threshold-based proposal at audit's final-call) for a future version. Not blocking; observer's clustering covers most of the same ground via convergence rule anyway.
**Cost**: design doc only at this point.

### LOW — Observer phase length / reader load
**Symptom**: observer phase body is the longest single phase (8 steps + 3 special rules + boundary callout authoring guidance). Risk: future authors copying it for other patterns will struggle.
**Fix**: nothing structural needed yet. Re-evaluate after the prototype has 5+ live runs to see which steps are doing work.

---

## Recommendations summary (ordered by leverage)

| Priority | Action | Files | Cost |
|---|---|---|---|
| HIGH | Add `boundary_violation` category to observer | observer-phase.md + 2 SKILL.md + meta-self-learning-skill-gen | 4 files |
| HIGH | Formalize `_theme_slug` in schema | observations_schema_v1.md | 1 file |
| MEDIUM | Document `friction_log` dual-writer coordination | run_history_schema_v1.md | 1 file |
| MEDIUM | Add `observer-paraphrased-user-input` to universal seed FAIL set | run_history_schema_v1.md + audit-phase.md + observer-phase.md | 3 files |
| LOW | Mark inlined boundary callout copies as "edit-template-and-mirror" | 2 SKILL.md files | 2 files |
| LOW | Plan Tier 2 promotion path for improvement_suggestions[] | SELF_LEARNING_SKILLS.md | design only |

**Total cost of HIGH+MEDIUM fixes**: 4 unique files (some appear in multiple rows), under 100 LOC of doc/schema edits, no behavioral changes to the actual runtime.

## Should we test the prototype now or fix first?

**My recommendation: test first, fix in parallel.**

Reasons:
- The 3 HIGH/MEDIUM weaknesses are all documentation/schema gaps, not runtime bugs. The system *runs* correctly today.
- The first live observer run on `shared-bug-gap-fix I-L1` will surface real signal on whether the prototype earns its keep — that's the bigger uncertainty.
- The HIGH fixes can be applied between runs without disturbing existing runs' data.

If a HIGH fix is later applied, no migration is needed: existing `observations.json` files are forward-compatible (field additions are tolerated by schema design).

## What this audit did NOT cover

- Domain-phase quality of either reference skill — out of scope.
- Cross-skill audit (overlaps with non-self-learning skills) — use `/meta-skill-audit`.
- LLM-judgment failure modes inside the observer's clustering pass — would require multiple live runs to characterize.
- Generator (`meta-self-learning-skill-gen`) interview UX — separate audit; this one is about the runtime pattern.
