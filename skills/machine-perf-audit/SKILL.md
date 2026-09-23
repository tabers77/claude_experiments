---
name: machine-perf-audit
description: Diagnose why a machine is slow and what disk/RAM/CPU can be recovered — bounded triage across seven lanes, ranked deep-dives into only the lanes that matter, every cost attributed to a named process or path with verbatim probe output, emitted as a permission-tiered remediation tracker. Strictly read-only — it never runs destructive commands. Keywords machine performance slow laptop slow computer disk full free up space out of disk space low RAM memory pressure memory compression high CPU pagefile thrash docker disk usage vhdx wsl 9p bind mount pip installed outside venv user-site orphan venv duplicate torch cache sprawl startup bloat defender scan reclaim space cleanup tuning baseline delta.
metadata:
  pattern: self-learning
  schema-version: 1
---

# Machine Perf Audit

Find out why a development machine is slow and what can actually be recovered, without breaking it. The skill runs a cheap bounded triage across seven lanes, ranks them by recoverable impact against effort and risk, deep-dives **only** the lanes that clear their evidence floor, attributes every cost to a named process or path, and emits a permission-tiered remediation tracker the user runs themselves. It is strictly read-only end to end: it probes, it reasons, it writes a plan — it never prunes, deletes, uninstalls, or reconfigures anything.

**Load-bearing principle**: read-only and evidence-bound. The skill NEVER executes a destructive or state-changing command; every recommendation cites verbatim probe output naming a specific process or path; every reclaim figure is labelled `apparent` or `host-level` and carries the command that verifies it; nothing on the protected-process registry is ever proposed for removal.

## Inputs

The user invokes the skill with one of:

| Shape | Example | Mode |
|---|---|---|
| (no arg) | `/machine-perf-audit` | `full` — triage all seven lanes, deep-dive the top-ranked |
| Lane name(s) | `python` · `disk,docker` | `lane` — triage all, but restrict deep-dive to the named lanes |
| `delta` | `delta` | `delta` — re-measure against the most recent baseline snapshot and report what moved |
| Free-text symptom | `everything crawls when docker is up` | `symptom` — triage all, weight ranking toward the described symptom |

If the input is none of the above, print the lane list from `LANES`, list the baseline snapshots found in `BASELINE_DIR`, and ask the user to pick a mode. Do NOT guess a mode from ambiguous text.

---

## Project config

Defaults target a Windows 11 corporate-managed developer laptop with WSL2 + Docker Desktop. Override per machine by editing this block — every reference to these names elsewhere in the skill resolves to the values defined here. Empty list / null means "skip the dependent check"; the skill never silently substitutes a guessed equivalent.

```yaml
PLATFORM: windows
  # v1 ships Windows probes (incl. WSL2 + Docker Desktop). Phase 1 gates every
  # probe on the detected platform. On a non-Windows host the skill records the
  # platform honestly and runs ONLY the lanes it has real probes for — it never
  # invents a "probably equivalent" command. Missing probes -> lane recorded as
  # `unprobed (no <platform> probe catalog)`, never as `clean`.

BASELINE_DIR: ~/.claude/machine-perf-audit
  # User-scoped ON PURPOSE. Snapshots carry hostname, machine serial, installed
  # software and user paths. NEVER write them into a repo — `documentation/` is
  # checked in. null -> delta reporting is skipped and Phase 2 records
  # "no baseline store configured".

TRACKER_OUTPUT: documentation/MACHINE_PERF_TRACKER.md
  # Where the remediation tracker is written, relative to the invoking project.
  # It names local paths and installed software — the skill warns the user to
  # review before committing it. null -> print the tracker to console only.

PROTECTED_PROCESSES:
  # Corporate-mandated agents. NEVER propose stopping, disabling, uninstalling,
  # killing, or self-excluding these. The ONLY permitted verbs against a name on
  # this list are: "ask IT to reschedule", "request exclusion", "observe",
  # "report". Any other verb is an automatic FAIL
  # (`suggested-touching-protected-corporate-agent`).
  - CcmExec                    # SCCM client
  - IntuneManagementExtension  # Intune
  - Sense                      # Defender for Endpoint
  - WinDefend                  # Defender AV service
  - MsMpEng                    # Defender scan engine
  - MDCoreSvc
  - MDDlpSvc                   # Defender DLP
  - PanGPS                     # GlobalProtect VPN
  - netclean-proactive
  - svcncpa                    # NetClean
  - KService                   # Kollective
  - mgssecsvc                  # Flexera
  - ndinit                     # Flexera
  - ndtrack                    # Flexera inventory scanner
  - AzInfoProtection           # Azure Information Protection

PROTECTED_DOCKER:
  named_volumes: all       # named volumes hold real database data
  running_containers: all
  # Keep-lists are COMPUTED from live inspection in Phase 5, never assumed and
  # never carried over from a previous run.

LANES: [disk, ram, cpu, io, docker, startup, python]

LANE_SELECTION_FLOOR:
  # Minimum triage signal for a lane to be ELIGIBLE for deep-dive. A lane below
  # its floor cannot be selected — selecting it anyway is an automatic FAIL
  # (`deep-dive-lane-not-justified-by-triage-evidence`).
  disk:    "free < 25% OR any single top-level tree > 5 GB"
  ram:     "free < 15% OR memory compression > 500 MB"
  cpu:     "any non-protected process > 1h cumulative CPU OR sustained load > 80%"
  io:      "host-boundary process > 30m cumulative CPU OR >0 bind mounts into running containers"
  docker:  "docker present AND (reclaimable > 5 GB OR (vhdx_on_disk_gb - docker_used_gb) > 10 GB)"
  startup: ">8 auto-start entries OR uptime > 7 days"
  python:  "user-site packages > 0 OR orphan venvs > 2 OR duplicate heavy wheels > 1"

DEEP_DIVE_MAX_LANES: 3
  # Cap on lanes deep-dived per run. The funnel's entire value is NOT probing
  # everything. Raise only when the user explicitly asks for a wider sweep.

CACHE_OWNER_QUERIES:
  # NEVER hardcode a cache path. Every path comes from its owning tool, queried
  # in this run. Using a remembered or assumed path is an automatic FAIL
  # (`assumed-cache-path-without-querying-owning-tool`).
  pip:         "pip cache dir"
  npm:         "npm config get cache"
  poetry:      "poetry config cache-dir"
  uv:          "uv cache dir"
  yarn:        "yarn cache dir"
  pnpm:        "pnpm store path"
  go:          "go env GOCACHE"
  cargo:       "echo the CARGO_HOME env var, else ~/.cargo"
  huggingface: "python -c \"from huggingface_hub.constants import HF_HUB_CACHE; print(HF_HUB_CACHE)\""
  torch:       "python -c \"import torch.hub; print(torch.hub.get_dir())\""
  playwright:  "playwright install --dry-run   (prints the browsers path)"

REPO_ROOTS:
  # Directories walked in the python lane for orphan venvs and duplicate wheels.
  # Empty list -> the orphan-venv and duplicate-wheel probes are skipped honestly.
  - "~/Documents/Repos"
  - "~/source"
  - "~/dev"

HEAVY_WHEELS:
  # Packages large enough that duplication across venvs is a headline finding.
  [torch, torchvision, torchaudio, tensorflow, nvidia-cudnn-cu12, nvidia-cublas-cu12,
   triton, jaxlib, onnxruntime-gpu, scipy, opencv-python]

ORDERING_CONSTRAINTS:
  # <action> MUST NOT appear before <after> in the emitted tracker. Violating
  # one is an automatic FAIL (`ordering-constraint-violated`).
  - action: "cap or shrink the pagefile"
    after:  "RAM-pressure fixes (memory reclaim config, browser/editor residency)"
    why:    "shrinking the pagefile while RAM is still exhausted risks OOM"
  - action: "compact or sparsify a VHDX"
    after:  "shutting the VM down (e.g. wsl --shutdown)"
    why:    "the disk file is locked while the VM is running"
  - action: "purge any cache"
    after:  "querying that cache's path from its owning tool"
    why:    "assumed paths purge the wrong directory or silently no-op"
  - action: "any docker image / builder prune"
    after:  "computing the keep-list from live containers and named volumes"
    why:    "a stopped-but-needed container's image is prune-eligible"

ELEVATION_DETECT: |
  ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

---

## Mid-run suggestion capture

The user can propose improvements to **this skill itself** at any point during a run, not only at the audit. The skill recognizes specific trigger prefixes; any user message that opens with one is captured verbatim into `improvement_suggestions[]` in `run_history.json`, then the run continues exactly where it was.

**Recognized trigger prefixes** (case-insensitive, on any line):

```
suggestion: <text>
improvement: <text>
for the skill: <text>
[suggestion] <text>
[skill-improvement] <text>
```

**Optional `[tag]` after the prefix**, used later for grouping:

```
suggestion: [5-python-lane] also inventory conda envs, not just venvs
improvement: [7-tiering] split the admin tier into "local admin" and "IT ticket"
```

**Capture protocol** (the skill follows this exactly):

0. **Ownership rule (single source of truth)**: when this skill is invoked with `invocation_mode=composed`, the suggestion is still captured **only into the deepest active skill's `improvement_suggestions[]`** — i.e. THIS skill's file, not the parent's. The parent's ledger phase looks up child suggestions cross-file at `quality_derived` computation time. Never duplicate a suggestion across two skill files.

   The captured entry records `parent` and `parent_run_ts` (when composed) so the parent can correlate it back to the right parent run. When standalone, both fields are null.

1. **Detect the prefix** at the start of the user's message (any of the five forms above; `[tag]` between the prefix and the text is optional). Anything that does NOT start with one of these prefixes is normal conversation — *not* a suggestion. Mid-run overrides ("skip the docker lane this time") go through the Phase 8 resolution flow, not this capture path.

2. **Record verbatim** into `improvement_suggestions[]`:
   ```json
   {
     "ts": "<iso8601-now>",
     "target": "<run input>",
     "phase": "<current phase number when the user spoke up>",
     "tag": "<optional, parsed from [brackets]>",
     "text": "<everything after the prefix and optional tag>",
     "sentiment": "<negative | aspirational | neutral>",
     "parent": "<parent skill name when composed, null when standalone>",
     "parent_run_ts": "<parent's started_at iso8601 when composed, null when standalone>",
     "applied_at": null,
     "applied_via": null
   }
   ```

   **Sentiment classification** — apply this keyword heuristic at capture time (case-insensitive substring match on the suggestion text):

   | Sentiment | Trigger keywords (any match wins) | What it means |
   |---|---|---|
   | `negative` | `broken`, `wrong`, `incorrect`, `missed`, `failed`, `bug`, `doesn't`, `does not`, `should not`, `shouldn't`, `regression`, `flaw`, `error`, `mistake` | User is flagging a problem with this run. Counts against `quality_derived`. |
   | `aspirational` | `would be nice`, `consider`, `could also`, `enhancement`, `add`, `nice to have`, `idea:`, `it would be cool`, `we should also`, `extend`, `support` | User is suggesting an enhancement. Does NOT count against `quality_derived`. |
   | `neutral` | none of the above match, OR matches in both lists | Ambiguous. Default fallback. Does NOT count against `quality_derived`. |

   Resolution rule: if both lists match, classify as `neutral`. If neither matches, `neutral` too. **Negative wins only when no aspirational keyword also matches**, so the heuristic stays conservative.

3. **Acknowledge** in one line:
   ```
   ✓ suggestion captured (phase X, tag=<tag-or-none>, sentiment=<negative|aspirational|neutral>): "<verbatim text>"
   ```

4. **Resume** the current phase from where it was. The capture does NOT alter the current run.

**What this is NOT**: not a phase override, not auto-applied, not a substitute for FAIL counters.

---

## Phase 0 — Freshness check (non-blocking)

Before running any domain work, briefly check how stale this skill has gotten. The check is **informational only** — it never blocks a run, and Phase 0.5 always proceeds after it.

The premise: a skill used heavily but never reviewed against the current state of Claude Code, peer skills, or its own domain will silently rot. This is especially live for a machine-tuning skill, whose probe commands and platform assumptions age with every OS and tooling release.

0. **Composition check — skip the freshness body entirely when invoked from another skill.** Parse the skill's invocation args for `invocation_mode=composed` (semicolon-separated `key=value` format). When present, **skip steps 1–4 of this phase** and proceed directly to step 5. Still stamp `started_at` for timing instrumentation — that fires unconditionally regardless of invocation mode.

   Default when the arg is absent or set to anything other than `composed` is `standalone` — all freshness steps below fire.

1. **Read** `skills/machine-perf-audit/run_history.json` → `validation_freshness`.
   - If the file is missing or the block is missing, initialize the block in-memory with:
     ```json
     {
       "created_at": "<now-iso8601>",
       "last_validated_at": "<now-iso8601>",
       "last_research_at": null,
       "last_overlap_check_at": null,
       "runs_since_validation": 0,
       "thresholds": { "runs": 10, "days": 21 },
       "review_log": []
     }
     ```
   - Phase 0 does NOT write to disk — it only reads. Persistence happens in Phase 10.

2. **Compute staleness**:
   - `days_since_validated = floor((now - last_validated_at) / 86400)` (in days).
   - `runs_since = validation_freshness.runs_since_validation`.

3. **Nudge condition — both must be true (AND, not OR)**:
   - `days_since_validated >= thresholds.days` (default 21), AND
   - `runs_since >= thresholds.runs` (default 10).

4. **When the nudge fires**, print exactly this one-line block at the top of the run, then continue:

   ```
   ⚠ Freshness: `machine-perf-audit` last validated <days_since_validated>d ago, <runs_since> runs since.
     Consider running, when you have a moment:
       /meta-discover-claude-features  — research improvements in this skill's domain
       /meta-skill-audit               — overlap check vs. other skills
     Then append a review_log[] entry to skills/machine-perf-audit/run_history.json → validation_freshness
     and bump last_validated_at + reset runs_since_validation to 0.
   ```

   **When the nudge does NOT fire**, print nothing at all. Silence is the success state. Do NOT print "freshness OK".

5. **Proceed to Phase 0.5 unconditionally.** The freshness check is never a hard gate.

---

## Phase 0.5 — Understand this run's expectations & build the run plan (non-skippable)

This phase runs **before any domain phase** and **after** the Phase 0 freshness check. It is numbered `0.5` so it sits between the freshness check and domain Phase 1 **without renumbering domain phases** — this keeps every phase-keyed FAIL tag stable.

Do exactly four things, in order:

0. **Stamp `started_at` if it isn't set yet.** Phase 0 normally stamps it; if freshness was skipped for any reason, stamp `started_at = run-start timestamp` here.

1. **Capture the request verbatim.** Read the user's invocation input and quote it verbatim into in-memory run state as `run_plan.request`. Never paraphrase — this is the artifact the audit and ledger consume. If invoked with `invocation_mode=composed`, quote whatever request text the parent passed (or note `composed; no explicit per-run request`).

2. **Start from the baseline — never a blank slate.** The baseline is this skill's domain phases, **1 through 8**. Enumerate them by id into `run_plan.baseline_steps`. You may NOT invent a plan that ignores the baseline; adaptation always starts from it.

3. **Classify every baseline step against this run's request.** For each baseline step, assign exactly one disposition:
   - **reuse** — run the step as written. (→ `run_plan.reused[]`)
   - **adapt** — run the step, modified for this run's intent; record a one-line `how`. (→ `run_plan.adapted[]`)
   - **skip** — do NOT run the step; record a one-line `justification` AND the step's `tier`. (→ `run_plan.skipped[]`)

   Then add **created** steps ONLY when the run genuinely needs work the baseline doesn't cover; record a one-line `why` and a synthetic id (e.g. `5b`). (→ `run_plan.created[]`)

   **Typical adaptations for this skill** (illustrative, not exhaustive):
   - `delta` mode → Phase 2 adapts to a full re-measure + diff; Phase 3 adapts to triage only the lanes that moved.
   - `lane` mode → Phase 3 still triages **all** lanes (cheap, and the ranking table is only honest with the full picture) but Phase 4 adapts to restrict the *selectable* set to the user's named lanes.
   - Phase 1 finds no Docker and no WSL → the `docker` and `io` lanes are recorded `unprobed (component absent)` — **never** `clean`.

   **Skip discipline:**
   - A **load-bearing** baseline step (Phases 1, 3, 4, 5, 6, 7) may be skipped *only* with an explicit, substantive justification. Skipping one without justification is an automatic FAIL (`plan-skipped-load-bearing-step-without-justification`).
   - **Procedural** steps (Phases 2, 8) skip freely — but the skip is still recorded.
   - Every baseline step MUST land in exactly one of reuse / adapt / skip. A baseline step in none of them is a **silent skip** → automatic FAIL (`plan-silent-skip`).

4. **Emit the run plan** to in-memory run state so the audit can reconcile it and the ledger can persist it. Print it as a short table before proceeding:

   ```
   Run plan for "<verbatim request>":
     baseline: [1, 2, 3, 4, 5, 6, 7, 8]
     reuse:    1, 3, 4, 5, 6, 7
     adapt:    2 — <how>
     skip:     8 — <justification> (tier: procedural)
     create:   5b — <why>
   ```

   This phase does NOT gate on an approval token. Proceed to the (non-skipped) domain phases immediately after printing.

**Non-skippable invariant:** Phase 0.5, the Phase 9 audit, and the Phase 10 ledger are machinery and can never appear in `run_plan.skipped[]`.

---

## Per-phase timing instrumentation (global rule)

Every domain phase stamps `phase_durations[<id>] = seconds_elapsed` into in-memory run state **as it exits**, using its literal id (`"1"`, `"2"`, … and any created sub-step id such as `"5b"`). Phase 0 (or Phase 0.5 when freshness is skipped) stamps `started_at` once at run start. Phase 10 computes `ended_at`, `duration_seconds`, and `quality_derived`. This is always-on instrumentation, not a toggle — do not omit it and do not fabricate it.

---

## Phase 1 — Platform gate & environment fingerprint

**Tier: load-bearing.** Every probe in Phase 3 and Phase 5 is gated on what this phase finds. Running a probe for a component recorded `absent` or `unknown` is an automatic FAIL (`probe-ran-without-platform-gate`).

1. **Detect the platform and refuse to improvise.** Establish OS family and version. If it does not match `PLATFORM`, record the mismatch verbatim and continue with ONLY the lanes for which this skill has a real probe catalog. Never translate a Windows probe into a "probably equivalent" command for another OS — record the lane `unprobed (no <platform> probe catalog)` instead.

   ```powershell
   Get-CimInstance Win32_OperatingSystem | Select-Object Caption, BuildNumber, Version, LastBootUpTime
   Get-CimInstance Win32_ComputerSystem  | Select-Object Manufacturer, Model, TotalPhysicalMemory
   Get-CimInstance Win32_Processor       | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
   ```

2. **Detect elevation.** Run `ELEVATION_DETECT`. Record `elevated: true|false`. This decides which tier Phase 7 can offer as self-serve, and it is NEVER a reason to attempt an elevated action — the skill is read-only regardless.

3. **Fingerprint each component** the lanes depend on. For each, record exactly one of `present` (with version), `absent`, or `unknown` (command exists but failed — capture the error verbatim). Never infer presence from the existence of a directory.

   | Component | Probe | Gates lane |
   |---|---|---|
   | WSL | `wsl --version` then `wsl -l -v` | io, docker |
   | Docker | `docker version --format json` (read `.Server.Version`) | docker, io |
   | Python | `python -c "import sys; print(sys.version)"` | python |
   | py launcher | `py -0p` | python |
   | conda | `conda --version` | python |
   | Node/npm | `node -v` then `npm -v` | python (cache sprawl) |
   | Defender | `Get-MpComputerStatus \| Select-Object AMServiceEnabled, AntivirusEnabled` | cpu, io |

4. **Inventory the managed agents.** Report which `PROTECTED_PROCESSES` entries exist and their state. This is an **observation**, and it exists so later phases can screen against it:

   ```powershell
   Get-Service | Where-Object { $_.Name -in @('CcmExec','Sense','WinDefend','PanGPS','ndtrack','KService') } |
     Select-Object Name, Status, StartType
   ```

5. **Emit the fingerprint** to run state as `fingerprint`, and print it as a compact table. Every Phase 5 probe declares the components it requires and is skipped (recorded, not silent) when a required component is not `present`.

**Exit**: stamp `phase_durations["1"]`.

**Evidence shape for the audit**: `fingerprint: os=<caption> build=<n>, elevated=<bool>, wsl=<state>, docker=<state>, python=<state>; protected agents found: <n>`

---

## Phase 2 — Baseline load & delta

**Tier: procedural.** Skippable with a recorded justification (e.g. first run on a machine with no baseline store).

1. **Load the most recent baseline.** List `BASELINE_DIR` for `*.json`, newest first. Read the newest. If the directory is missing or empty, record `baseline: none (first run)` and continue — do NOT create the directory here; the Phase 9-approved write does that.

2. **Capture the current metric vector.** These are the same measurements the tracker's re-measure block uses, so a later run can diff them:

   ```powershell
   Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" |
     Select-Object @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,1)}},
                   @{n='TotalGB';e={[math]::Round($_.Size/1GB,1)}},
                   @{n='PctFree';e={[math]::Round(100*$_.FreeSpace/$_.Size,1)}}

   Get-CimInstance Win32_OperatingSystem |
     Select-Object @{n='FreeRAM_GB';e={[math]::Round($_.FreePhysicalMemory/1MB,1)}},
                   @{n='TotalRAM_GB';e={[math]::Round($_.TotalVisibleMemorySize/1MB,1)}},
                   @{n='UptimeDays';e={[math]::Round(((Get-Date)-$_.LastBootUpTime).TotalDays,2)}}

   Get-Process MemCompression -ErrorAction SilentlyContinue | Select-Object Name, WS
   Get-CimInstance Win32_PageFileUsage | Select-Object AllocatedBaseSize, CurrentUsage, PeakUsage
   ```

3. **Compute the delta** for every metric present in both the baseline and now. Print a table `metric | baseline (<date>) | now | Δ`. Flag any metric that **regressed** since the last run — a cache that regrew, a VHDX that ratcheted back up, free RAM that fell. A regression is the strongest evidence that a previous fix did not hold, and it means the tracker needs a **durable-config** action, not another one-off purge.

4. In `delta` mode, this phase's output IS the headline: report what moved and do not expand scope unless a regression crosses a `LANE_SELECTION_FLOOR`.

**Exit**: stamp `phase_durations["2"]`.

**Evidence shape for the audit**: `baseline=<file-or-none>; metrics captured=<n>; regressions=<list or none>`

---

## Phase 3 — Bounded triage across the seven lanes

**Tier: load-bearing.** This phase consumes user input when the mode is `lane` or `symptom` — that input MUST be quoted verbatim in the audit, never paraphrased.

Run a small, cheap, bounded set of probes — roughly one or two per lane, a dozen total. The goal is a **symptom vector**, not a diagnosis. Do NOT deep-dive here; that is Phase 5's job, and only for lanes that earn it.

1. **Record the scoping input verbatim** when the mode is `lane` or `symptom`. Example: `user scoping input verbatim: "python,docker"`. Triage **all** lanes regardless — triage is cheap and Phase 4's ranking table is only honest with the full picture. The scoping input restricts what Phase 4 may *select*, not what Phase 3 measures.

2. **Run the triage probes**, respecting the Phase 1 fingerprint. Each lane yields one headline metric plus the raw output that produced it.

   | Lane | Headline metric | Triage probe |
   |---|---|---|
   | disk | `C:` free % + largest top-level tree | `Get-CimInstance Win32_LogicalDisk`; per-directory size bounded to depth 1 |
   | ram | free RAM % + memory-compression MB | `Get-CimInstance Win32_OperatingSystem`; `Get-Process MemCompression` |
   | cpu | top non-protected cumulative CPU-time process | `Get-Process \| Sort-Object CPU -Descending \| Select-Object -First 5 Name, Id, CPU` |
   | io | host-boundary CPU burn | `Get-Process dllhost, vmmem, vmmemWSL -ErrorAction SilentlyContinue \| Select-Object Name, Id, CPU` |
   | docker | reclaimable GB + VHDX-vs-used gap | `docker system df`; `Get-ChildItem $env:LOCALAPPDATA\Docker -Recurse -Filter *.vhdx` |
   | startup | auto-start entry count | `Get-ItemProperty HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` + the HKLM equivalent — count only |
   | python | user-site package count + venv count | `python -m site --user-site`; `python -c "import sys; print(sys.prefix != sys.base_prefix)"` |

   **Cumulative CPU time, not instantaneous percent.** A process at 2% right now that has burned 20 hours since boot is the finding; a process spiking to 40% for three seconds is not. This is the single most common misread in machine tuning.

3. **Screen every CPU/IO finding against `PROTECTED_PROCESSES` immediately.** A protected agent that tops the list is a legitimate *observation* and stays in the report — but it is tagged `protected` from this moment on, so no later phase can turn it into a removal action.

4. **Emit the symptom vector.** One row per lane: headline metric, its `LANE_SELECTION_FLOOR`, whether the floor is cleared, and the state (`measured` / `unprobed (component absent)` / `unprobed (no platform catalog)`). An unprobed lane is NEVER reported as clean.

   ```
   Lane     | Headline                              | Floor                    | Clears? | State
   ---------|---------------------------------------|--------------------------|---------|---------
   disk     | 19.3% free (91.8 of 475.5 GB)         | free < 25%               | YES     | measured
   python   | 41 user-site packages, 14 venvs       | user-site > 0            | YES     | measured
   startup  | 6 auto-start entries, uptime 1.2d     | >8 entries OR >7d uptime | no      | measured
   io       | —                                     | —                        | —       | unprobed (WSL absent)
   ```

**Exit**: stamp `phase_durations["3"]`.

**Evidence shape for the audit**: `lanes triaged: <n>/7; floors cleared: <list>; unprobed: <list with reason>; user scoping input verbatim: "<literal quote>"`

---

## Phase 4 — Rank lanes & select the deep-dive set

**Tier: load-bearing.** This phase is the funnel. Selecting a lane whose ranking row cites no Phase 3 evidence — or cites a metric below the lane's floor — is an automatic FAIL (`deep-dive-lane-not-justified-by-triage-evidence`).

1. **Score every lane that cleared its floor**:

   ```
   score = (recoverable_impact × confidence) / (effort × risk)
   ```

   | Factor | Scale | How to set it |
   |---|---|---|
   | `recoverable_impact` | 0–10 | GB recoverable, or the equivalent for a non-disk lane (RAM GB returned, CPU-hours/day reclaimed). Use the **host-level** figure wherever the two differ — see Phase 6. |
   | `confidence` | 0.0–1.0 | How directly the Phase 3 evidence supports the estimate. A measured directory size is 1.0; an inferred "probably regrew" is 0.4. |
   | `effort` | 1–5 | 1 = one command; 5 = an IT ticket with a wait. |
   | `risk` | 1–5 | 1 = reversible cache purge; 5 = could destroy data or break a managed agent. |

2. **Weight toward the stated symptom** when the mode is `symptom`. Quote the symptom verbatim, name which lanes it points at, and say by how much you weighted them. Never let the weighting promote a lane that did not clear its floor.

3. **Print the full ranking table — including lanes NOT selected, each with its reason.** Silent omission is how a funnel degrades into a guess.

   ```
   Rank | Lane    | Impact | Conf | Effort | Risk | Score | Selected | Basis / reason
   -----|---------|--------|------|--------|------|-------|----------|--------------------------------------
   1    | python  | 7      | 1.0  | 1      | 2    | 3.50  | YES      | Phase 3: 41 user-site pkgs (floor >0)
   2    | docker  | 9      | 0.9  | 2      | 3    | 1.35  | YES      | Phase 3: 67.5 GB reclaimable (floor >5 GB)
   -    | startup | 2      | 0.8  | 1      | 1    | 1.60  | no       | below floor: 6 entries, uptime 1.2d
   -    | io      | —      | —    | —      | —    | —     | no       | unprobed: WSL absent (Phase 1)
   ```

4. **Select at most `DEEP_DIVE_MAX_LANES`**, highest score first, restricted to the user's named lanes when the mode is `lane`. If the user named a lane that did not clear its floor, say so explicitly and ask whether to deep-dive it anyway — never silently include it, never silently drop it.

**Exit**: stamp `phase_durations["4"]`.

**Evidence shape for the audit**: `ranked <n> lanes; selected: <list> (cap <DEEP_DIVE_MAX_LANES>); each selection cites a Phase 3 metric + floor; not-selected reasons recorded: <n>`

---

## Phase 5 — Deep-dive probes, selected lanes only

**Tier: load-bearing.** Run the probe catalog for **only** the lanes Phase 4 selected. Every probe declares the Phase 1 components it requires; running one whose component is not `present` is an automatic FAIL (`probe-ran-without-platform-gate`).

**All probes in this phase are read-only.** None of them deletes, prunes, stops, uninstalls, or reconfigures. If a probe's natural form has a destructive flag, use the inspection form instead (`docker system df -v`, never `docker system prune`).

### 5.disk — Disk pressure  *(requires: none)*

```powershell
# Top-level trees, bounded — do not recurse the whole volume
Get-ChildItem C:\ -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object {
  [PSCustomObject]@{ Path=$_.FullName
    GB=[math]::Round((Get-ChildItem $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue |
        Measure-Object Length -Sum).Sum/1GB,2) } } | Sort-Object GB -Descending | Select-Object -First 15

Get-ChildItem C:\Windows\WinSxS -Force -ErrorAction SilentlyContinue | Measure-Object -Sum Length
Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage, PeakUsage
Get-ItemProperty 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy' -EA SilentlyContinue
```

Report the **pagefile allocated-vs-peak gap** explicitly: an allocation far above observed peak usage is recoverable, but only under the Phase 7 ordering constraint that RAM fixes land first.

### 5.ram — Memory pressure  *(requires: none)*

```powershell
Get-Process | Group-Object ProcessName | ForEach-Object {
  [PSCustomObject]@{ Name=$_.Name; Count=$_.Count
    WS_MB=[math]::Round(($_.Group | Measure-Object WorkingSet64 -Sum).Sum/1MB,0) } } |
  Sort-Object WS_MB -Descending | Select-Object -First 15

Get-Process MemCompression -EA SilentlyContinue | Select-Object Name, @{n='MB';e={[math]::Round($_.WS/1MB,0)}}
Get-Content "$env:USERPROFILE\.wslconfig" -EA SilentlyContinue
```

**Memory compression is the exhaustion tell.** A large compression working set means Windows is compressing pages rather than freeing them — the machine is out of RAM regardless of what the free-MB number says. Report process *families* (grouped by name with a count), not individual PIDs: "Edge — 23 processes, 2,609 MB" is actionable; 23 separate rows are not.

### 5.cpu — CPU burn  *(requires: none)*

```powershell
Get-Process | Where-Object { $_.CPU -gt 60 } | Sort-Object CPU -Descending |
  Select-Object Name, Id, @{n='CPU_Hours';e={[math]::Round($_.CPU/3600,2)}},
                @{n='WS_MB';e={[math]::Round($_.WorkingSet64/1MB,0)}}, StartTime

Get-ScheduledTask | Where-Object State -eq 'Running' | Select-Object TaskName, TaskPath
Get-MpPreference | Select-Object ScanAvgCPULoadFactor, DisableRealtimeMonitoring
```

Rank by **cumulative CPU hours since process start**, and divide by uptime to get a per-day burn rate. Screen every row against `PROTECTED_PROCESSES` before it reaches Phase 7 — a protected agent's burn is reported with the only permitted verbs (`ask IT to reschedule`, `request exclusion`).

### 5.io — Host-boundary tax  *(requires: WSL present OR Docker present)*

```powershell
Get-Process dllhost -EA SilentlyContinue | Sort-Object CPU -Descending |
  Select-Object Id, @{n='CPU_Hours';e={[math]::Round($_.CPU/3600,2)}}
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```
```bash
# Bind mounts crossing the Windows <-> Linux boundary, per running container.
# Read `.Name` and each `.Mounts[]` entry's `.Type` and `.Source` from the JSON.
docker ps -q | xargs -r docker inspect --format json
```

A `dllhost` with hours of cumulative CPU is the WSL 9P file server: every container file read is crossing the host boundary. Pair that number with the bind-mount inventory — each `bind` mount whose `Source` is a Windows path is a contributor. The fix belongs in the tracker as a **configuration** action (move the working tree inside the Linux filesystem, or switch to a named volume), never as a deletion.

### 5.docker — Container bloat  *(requires: Docker present)*

```bash
docker system df -v
docker ps -a --format json       # id, names, image, state — running AND stopped
docker volume ls --format json   # named volumes: these hold real data
docker images --format json      # repository, tag, id, size
```
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Docker" -Recurse -Filter *.vhdx -EA SilentlyContinue |
  Select-Object FullName, @{n='OnDiskGB';e={[math]::Round($_.Length/1GB,2)}}
fsutil sparse queryflag "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"
```

**Compute the keep-list — never assume one.** Build it mechanically, in this order:

1. Every image referenced by **any** container, running or stopped (`docker ps -a` → image ids). A stopped container's image is prune-eligible by default and this is exactly how a needed image gets destroyed.
2. Every image backing a container attached to a **named volume** (those volumes hold real data).
3. Every image the user names in the Phase 8 resolution gate.

Everything outside the computed keep-list is a *candidate*, and it reaches Phase 7 as an **explicit per-image `docker rmi <repo:tag>` list**, never as a blanket `prune -a`. Reconcile the disk file against the engine's own accounting and report the gap as its own line item:

```
vhdx_on_disk_gb − docker_used_gb = trapped_gb
```

That trapped space is real but it is **not** returned to the host by pruning — only by compacting the disk file, which carries its own ordering constraint.

### 5.startup — Startup & residency  *(requires: none)*

```powershell
Get-ItemProperty 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -EA SilentlyContinue
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -EA SilentlyContinue
Get-ItemProperty 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run' -EA SilentlyContinue
Get-ScheduledTask | Where-Object { $_.Triggers.CimClass.CimClassName -match 'Logon' } | Select-Object TaskName
```

Cross-reference each entry against the Phase 5.ram and 5.cpu findings so the tracker can say *why* an entry is worth removing, not just that it exists. Screen against `PROTECTED_PROCESSES`.

### 5.python — Python / dev hygiene  *(requires: Python present)*

This lane answers "are packages installed outside a venv, and what else has leaked?" Run every probe; report each finding separately.

**a. Is the active interpreter a venv?**
```bash
python -c "import sys; print('VENV' if sys.prefix != sys.base_prefix else 'BASE', sys.prefix)"
```

**b. Packages installed outside a venv (the actual leak).**
```bash
python -m site --user-site
python -m pip list --user --format=json
```
Size the user-site directory and count the packages. These shadow venv packages at import time and are the usual cause of "works on my machine". Report the count, the total size, and the five largest.

**c. Is the bare-pip guard set?**
```bash
python -c "import os; print('PIP_REQUIRE_VIRTUALENV=' + os.environ.get('PIP_REQUIRE_VIRTUALENV','UNSET'))"
python -m pip config list
```
When unset, this is a **prevention** finding, not a cleanup one: setting it makes a future bare `pip install` fail loudly instead of silently leaking into user-site. It belongs in the tracker's no-admin tier as a config action.

**d. Interpreter sprawl.**
```bash
where python ; where pip ; py -0p ; conda env list
```
Flag the Microsoft Store `WindowsApps\python.exe` stub if present, and any case where `where python` and `where pip` resolve to different installations — that mismatch is why "pip installed it but python can't import it".

**e. `PYTHONPATH` pollution.**
```powershell
$env:PYTHONPATH
```

**f. Orphan venvs.**  *(requires: REPO_ROOTS non-empty)*
Walk each `REPO_ROOTS` entry for directories containing `pyvenv.cfg`. For each: size, last-write time, and whether the parent repository has recent commits (`git -C <repo> log -1 --format=%cI`). A venv whose repo has been untouched for months is recoverable space with near-zero risk — and it is listed **per venv with its own path**, never as a blanket "delete all venvs".

**g. Duplicated heavy wheels.**
For every venv found in (f), inspect `Lib/site-packages` (Windows) or `lib/python*/site-packages` for each name in `HEAVY_WHEELS`; record size and version per venv. Report the total duplicated footprint. The fix is a **shared cache or a tool like `uv`**, not mass deletion — say so, because deleting a venv's `torch` breaks that project.

**h. Cache sprawl — every path from its owning tool.**
Run each command in `CACHE_OWNER_QUERIES` whose tool Phase 1 found `present`, then size the path it returns. **Never** write a cache path into the report that did not come out of one of these commands in this run. Assumed paths are wrong often enough to matter: a cache can live under `LOCALAPPDATA` on one machine and `APPDATA` on another, and purging the assumed one silently does nothing while the real one keeps growing.

**Exit**: stamp `phase_durations["5"]`.

**Evidence shape for the audit**: `lanes deep-dived: <list>; probes run: <n>; probes skipped (component absent): <n with reason>; cache paths resolved via owning tool: <n>/<n>`

---

## Phase 6 — Attribution & reclaim accounting

**Tier: load-bearing.** This phase converts probe output into findings that can be defended. A finding that cannot name its process or path does not survive this phase.

1. **Attribute every cost.** Each finding must carry one of:
   - a **named process**: name + PID + cumulative CPU hours + working set, or
   - a **named path**: full path + measured size + the command that measured it.

   "Docker is using a lot of space" is not a finding. "`%LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx` is 113.32 GB on disk while the engine accounts for 73.7 GB" is.

2. **Label every reclaim figure `apparent` or `host-level`, and attach its verification command.** This is the accounting rule the whole skill turns on:

   | Label | Meaning | Example |
   |---|---|---|
   | `host-level` | The host's free space actually increases by this much. | Deleting a directory on `C:` |
   | `apparent` | Space is freed *inside* a guest filesystem, VM disk, or container store. The host sees nothing until a separate compaction step runs. | `docker image rm`, `docker builder prune`, any guest-side delete |

   A figure sourced from a guest-internal tool (`docker system df`, a guest `df`) and presented as a host-drive gain is an automatic FAIL (`claimed-space-freed-without-host-level-remeasure`). Each figure carries the command that will prove it afterwards — typically the `C:` free-space query from Phase 2.

3. **Sum the two totals separately** and print both. Never add them together:

   ```
   Recoverable (host-level, verified by re-measure) ....... <n> GB
   Recoverable (apparent — inside VHDX/guest, needs compaction) .. <n> GB
   Currently trapped (freed inside the disk file, not returned) ... <n> GB
   ```

4. **Screen every finding against `PROTECTED_PROCESSES` one final time** before it can become an action. A protected process keeps its finding row and its measured cost, but its only permitted verbs are `ask IT to reschedule`, `request exclusion`, `observe`, `report`.

5. **Mark each finding `durable` or `one-off`.** A cache purge is one-off — it regrows. A config change (a memory-reclaim setting, `PIP_REQUIRE_VIRTUALENV`, a Defender exclusion, moving a working tree off the host boundary) is durable. When Phase 2 reported a regression on a metric, the corresponding finding MUST carry a durable action, not a repeat of the one-off purge that already failed to hold.

**Exit**: stamp `phase_durations["6"]`.

**Evidence shape for the audit**: `findings: <n>; each attributed to process-or-path: <yes/no>; host-level total <n> GB / apparent total <n> GB / trapped <n> GB; protected-screened: <n> rows`

---

## Phase 7 — Assemble the permission-tiered remediation plan

**Tier: load-bearing.** Build the plan in memory. **Do not write it yet** — the Phase 9 approval token gates the write.

1. **Sort every action into exactly one tier:**

   | Tier | Meaning |
   |---|---|
   | **A — no admin** | The user can run it now, in their own session. |
   | **B — local admin** | Needs an elevated shell. Offered only as an instruction; the skill never elevates. |
   | **C — IT ticket** | Managed-policy territory: Defender exclusions, scan scheduling, component cleanup, OS-level installs. Phrased as a request, with the justification evidence attached. |

2. **Give every action row the same shape:**

   ```
   ID | Action | Expected (host-level / apparent) | Risk | Keep-list | Verify | Prereq
   ```

   - **Keep-list** is mandatory and non-empty for any destructive command, computed in Phase 5. A destructive command reaching the plan without one is an automatic FAIL (`recommended-destructive-prune-without-computed-keep-list`). Destructive here means any of: `prune`, `rmi`, `rm -rf`, `Remove-Item -Recurse`, `--volumes`, `unregister`, an uninstaller, or a registry delete.
   - **Verify** is the exact command that proves the action worked — normally the Phase 2 metric query for the affected metric.
   - **Prereq** is any `ORDERING_CONSTRAINTS` dependency.

3. **Enforce `ORDERING_CONSTRAINTS` as a topological sort.** Every action must appear after its prerequisite. Emitting one out of order is an automatic FAIL (`ordering-constraint-violated`). Where a constraint cannot be satisfied (the prerequisite is in a tier the user can't reach), say so on the row and mark the action **blocked**, rather than reordering around it.

4. **Prefer durable over one-off.** When a finding has both a purge and a config fix, list the config fix first and note that the purge alone will regrow.

5. **Render the `DO NOT TOUCH` section** from `PROTECTED_PROCESSES`, listing each one found on this machine with its observed cost. This section exists so the reader understands why an expensive process is not on the action list.

6. **Render the tracker document in memory**, matching the reference exemplar's proven layout:

   ```
   ===============================================================================
    MACHINE PERF TRACKER — <hostname>
   ===============================================================================
    Machine   : <model> | <cpu> | <ram> | <disk>
    OS        : <caption> <build>
    Audited   : <date>
    Elevation : <yes/no>
    STATUS KEY:  [ ] todo   [~] in progress   [x] done   [!] blocked   [-] skipped

    BASELINE          <the metric vector, with Δ vs the previous snapshot>
    TRIAGE            <the seven-lane symptom vector>
    RANKING           <the full table, incl. lanes not selected and why>

    SECTION A — NO ADMIN
    SECTION B — LOCAL ADMIN
    SECTION C — IT TICKET
    DO NOT TOUCH      <protected agents + observed cost>
    RESULTS LOG       <empty rows for the user to fill as they execute>
    QUICK RE-MEASURE  <the Phase 2 commands, paste-ready>
   ```

   The **RESULTS LOG** is the point of the format: expected vs *actual* per action, so the next run can tell which fixes held.

**Exit**: stamp `phase_durations["7"]`.

**Evidence shape for the audit**: `actions: A=<n> B=<n> C=<n>; destructive actions with computed keep-list: <n>/<n>; ordering constraints satisfied: <n>/<n>; blocked: <n>`

---

## Phase 8 — User resolution gate (HARD-STOP before audit)

**Tier: procedural.** This phase consumes user input — it MUST be quoted verbatim in the audit, never paraphrased.

1. **Surface every action that needs a human judgment call.** An action qualifies when any of these hold:
   - `risk >= 3`
   - it removes data that must be re-downloaded (model weights, browser bundles, images from a remote registry)
   - it uninstalls an application
   - it touches a repository working tree
   - it is marked **blocked** by an unsatisfied ordering constraint

2. **Present each one individually** with its measured cost, its risk, and what it costs to undo:

   ```
   [R1] Remove ~/.cache/huggingface (7.07 GB, host-level)
        Undo cost: re-downloads on the next from_pretrained() call, over VPN.
        Resolve: keep / do / defer
   ```

3. **Require an explicit per-item resolution.** Silence is not a resolution. A blanket "ok" is not a resolution. If the user answers in bulk, map their answer onto each item and re-display the mapping for confirmation.

4. **Record every resolution verbatim** and apply it to the plan: `defer` moves the action to a `Deferred` section with the reason attached; `keep` drops it entirely and records why.

5. **HARD-STOP.** Do not proceed to Phase 9 until every surfaced item has an explicit resolution. Any item surfaced but unresolved when the audit runs is an `audit-no-explicit-approval-wait` occurrence.

**Exit**: stamp `phase_durations["8"]`.

**Evidence shape for the audit**: `surfaced: <n>; resolved-with-explicit-choice: <n>; user input verbatim: "<literal quote>"`

---

## Phase 9 — Pre-action self-audit (CHECKPOINT, blocking)

The audit runs **before** the doc-edit. Doc-edit cannot fire until the user explicitly confirms or corrects every audit row. Goal: verbatim, falsifiable evidence — never the skill's interpretation of user intent.

1. **Walk every phase that ran in this session** and emit a structured block. Each verdict MUST cite **objective evidence**: a tool call observed, a command output, a file diff, or a **literal quote** from the user. **Never paraphrase user input.** If the user said "tracker approved" with no per-item resolution, record `user said: "tracker approved" (no per-item resolution)` — do NOT invent a justification, do NOT summarise intent.

   ```
   Self-audit for run on <input> at <ts>:
   - Phase 1 [pass]      | fingerprint: os=<caption> build=<n>, elevated=<bool>, wsl=<state>, docker=<state>, python=<state>; protected agents found: <n>
   - Phase 2 [pass]      | baseline=<file-or-none>; metrics captured=<n>; regressions=<list or none>
   - Phase 3 [pass]      | lanes triaged: <n>/7; floors cleared: <list>; unprobed: <list with reason>
                           user scoping input verbatim: "<literal quote>"
   - Phase 4 [pass]      | ranked <n> lanes; selected: <list>; each selection cites a Phase 3 metric + floor; not-selected reasons: <n>
   - Phase 5 [pass]      | lanes deep-dived: <list>; probes run: <n>; skipped (component absent): <n>; cache paths from owning tool: <n>/<n>
   - Phase 6 [pass]      | findings: <n>; host-level <n> GB / apparent <n> GB / trapped <n> GB; protected-screened: <n>
   - Phase 7 [pass]      | actions A=<n> B=<n> C=<n>; destructive with keep-list: <n>/<n>; ordering satisfied: <n>/<n>
   - Phase 8 [pass|FAIL] | surfaced: <n> / resolved-with-explicit-choice: <n>
                           user input verbatim: "<literal quote>"
   ```

   Each row format: `- Phase X [pass|FAIL] | <evidence>` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input.

1a. **Run-plan reconciliation.** The audit walks the **Phase 0.5 run plan**, not a fixed phase list:
   - Emit one row per **executed** step (every entry in `run_plan.reused[]`, `run_plan.adapted[]`, `run_plan.created[]`) — same verbatim-evidence rules as step 1.
   - Emit one **skip-justification row** per **skipped** baseline step: `- Phase X [skipped] | reason: "<justification from run_plan.skipped[]>" (tier: <tier>)`.
   - **Silent-skip check:** every baseline step in `run_plan.baseline_steps` MUST appear in exactly one of the executed rows or the skip rows. A baseline step absent from both is a **silent skip** → mark FAIL with tag `plan-silent-skip`.
   - **Load-bearing-skip check:** any load-bearing baseline step in `run_plan.skipped[]` whose justification is empty or a placeholder (`n/a`, `-`, `none`, whitespace) → mark FAIL with tag `plan-skipped-load-bearing-step-without-justification`.

   The non-skippable phases (Phase 0.5, this audit, the ledger) are never expected as skip rows; if any appears in `run_plan.skipped[]`, mark FAIL.

2. **FAIL detection rules** — these trigger automatically; the skill cannot mark `pass` without satisfying them:

   **Universal FAIL rules:**
   - **`audit-paraphrased-user-input`** (load-bearing, threshold=1): any audit row that paraphrases user intent rather than quoting verbatim.
   - **`audit-no-explicit-approval-wait`** (procedural, threshold=2): skill advanced past a user-gate phase without observing the literal approval token.
   - **`tool-claim-without-call`** (load-bearing, threshold=1): audit row says "ran X" / "probed Y" but no corresponding tool call observed in this session.

   **Adaptive-execution FAIL rules:**
   - **`plan-silent-skip`** (load-bearing, threshold=1): a baseline step is absent from both the executed rows and the skip-justification rows.
   - **`plan-skipped-load-bearing-step-without-justification`** (load-bearing, threshold=1): a load-bearing baseline step appears in `run_plan.skipped[]` with an empty or placeholder justification.

   **Domain FAIL rules:**

   - **`recommended-destructive-prune-without-computed-keep-list`** (load-bearing, threshold=1): the Phase 7 plan contains a destructive command (`prune`, `rmi`, `rm -rf`, `Remove-Item -Recurse`, `--volumes`, `unregister`, an uninstaller, a registry delete) whose action row has an empty or absent keep-list, OR whose keep-list was not derived from a Phase 5 probe output observed in this session.
   - **`claimed-space-freed-without-host-level-remeasure`** (load-bearing, threshold=1): any reclaim figure asserted without an `apparent` / `host-level` label and a verification command, OR a figure sourced from a guest-internal tool (`docker system df`, guest `df`) presented as a host-drive gain.
   - **`suggested-touching-protected-corporate-agent`** (load-bearing, threshold=1): an action row names a `PROTECTED_PROCESSES` entry with a verb outside {`ask IT to reschedule`, `request exclusion`, `observe`, `report`}.
   - **`assumed-cache-path-without-querying-owning-tool`** (load-bearing, threshold=1): a cache path appears in the plan with no corresponding `CACHE_OWNER_QUERIES` invocation in this session's tool-call trace.
   - **`deep-dive-lane-not-justified-by-triage-evidence`** (load-bearing, threshold=1): a lane in Phase 4's selected set whose ranking row cites no Phase 3 metric, or cites a metric below that lane's `LANE_SELECTION_FLOOR`.
   - **`probe-ran-without-platform-gate`** (load-bearing, threshold=1): a Phase 5 probe executed for a component Phase 1 recorded `absent` or `unknown`, or Phase 5 ran with no Phase 1 fingerprint in run state.
   - **`ordering-constraint-violated`** (load-bearing, threshold=1): the emitted tracker lists an action before one of its `ORDERING_CONSTRAINTS` prerequisites.

3. **Show the audit and ask the user to confirm OR correct every row.** The audit is NOT approved on silence or a partial answer. The skill must wait for the user to:
   - **confirm** each row as written, OR
   - **dictate corrections** (which the skill applies verbatim and re-displays the audit), OR
   - **mark a row FAIL with a tag** (which the skill records).

4. **Approval gate**: the doc-edit cannot fire until the user explicitly types `tracker approved` (case-insensitive). Silence, "looks good", "ok", "proceed", or partial responses are NOT approval.

   On approval, and only then, perform the terminal action:
   - Write the tracker to `TRACKER_OUTPUT`.
   - Write the baseline snapshot to `BASELINE_DIR/<iso-date>.json`, creating the directory if needed.
   - Remind the user in one line that the tracker names local paths and installed software, and to review it before committing.

5. **Suggestion review (final-call)** — runs only after the approval token is received, before the ledger phase fires. Surface every entry captured during this run, then offer a final chance to add more:

   ```
   Suggestions captured during this run (N total):
     1. [phase X, tag=<tag-or-none>] "<verbatim text>"
     ...

   Any final suggestions to add? Use the same trigger-prefix syntax (or type `done` to skip):
     - suggestion: <text>
     - improvement: <text>
     - for the skill: <text>
     - [suggestion] <text>
   ```

   Append any final entries to `improvement_suggestions[]` with `phase: "audit"`. If the user types `done`, proceed to the ledger. If they add more, capture each, then re-prompt until `done`. Silence is NOT advancement — wait for `done`.

---

## Phase 10 — Update the run-history ledger

Persist the audit so failure patterns become evidence over time.

1. **Read** `skills/machine-perf-audit/run_history.json`. Initialize if missing per the schema in `library/templates/self-learning-skill/run_history_schema_v1.md`.

2. **Append** the run summary to `runs[]`:
   ```json
   {
     "ts": "<iso8601 of this ledger write — same as ended_at>",
     "target": "<input>",
     "outcome": "<closed|paused|aborted|in-progress>",
     "phases_failed": ["<tag>", ...],
     "started_at": "<iso8601 captured at run start>",
     "ended_at": "<iso8601-now>",
     "duration_seconds": <ended_at - started_at, integer seconds>,
     "phase_durations": {"1": <seconds>, "2": <seconds>, "...": "..."},
     "quality_derived": "<clean|partial|failed|incomplete>",
     "invocation_mode": "<standalone | composed>",
     "parent": "<parent-skill-name | null>",
     "parent_run_ts": "<iso8601 of parent's started_at | null>",
     "run_plan": {
       "request": "<verbatim user request from Phase 0.5>",
       "baseline_steps": ["1","2","3","4","5","6","7","8"],
       "reused": ["1"],
       "adapted": [{"step": "2", "how": "<one line>"}],
       "skipped": [{"step": "8", "justification": "<one line>", "tier": "procedural"}],
       "created": [{"step": "5b", "why": "<one line>"}]
     },
     "lanes_selected": ["<lane>", "..."],
     "reclaim_host_level_gb": <number>,
     "reclaim_apparent_gb": <number>
   }
   ```

   The three composition fields come from the skill's invocation args. Parse `invocation_mode=composed; parent=<name>; parent_run_ts=<ts>` at run start. When no `invocation_mode` arg is present, default to `invocation_mode: "standalone"` with `parent: null` and `parent_run_ts: null`.

   The skill tracks three pieces of running state across phases (in-memory):

   | State | Set by | Used here |
   |---|---|---|
   | `started_at` | Phase 0 (or Phase 0.5 if freshness skipped), before any work. | Emit verbatim. |
   | `phase_durations` | Each phase stamps `phase_durations[<id>] = seconds_elapsed` as it exits. | Emit verbatim. |
   | `ended_at` | Set NOW, at the top of this ledger phase. | Compute `duration_seconds`. |

   **`quality_derived` is computed mechanically:**
   - `clean` ← `outcome == "closed"` AND `phases_failed` is empty AND no negative-sentiment suggestion exists for this run's window.
   - `partial` ← `outcome == "closed"` AND (`phases_failed` non-empty OR at least one negative-sentiment suggestion exists for this run's window).
   - `failed` ← `outcome == "aborted"`.
   - `incomplete` ← `outcome == "paused"` OR `"in-progress"`.

   **Cross-skill lookup (only when `invocation_mode == "standalone"`)**: a negative-sentiment suggestion captured inside a composed child skill belongs to the child's file. Check each composed child's history file for negative-sentiment entries within `[started_at, ended_at]` whose `parent_run_ts == this_run.started_at`. This skill composes nothing at v1, so the lookup is a no-op until that changes. If a child's file is missing or unreadable, log to `friction_log[]` and proceed.

   If `started_at` was not recorded, omit `started_at`, `ended_at`, `duration_seconds`, `phase_durations`, and `quality_derived` entirely. Do NOT fabricate timing data.

3. **For each FAIL tag** observed in this run:
   - Increment `fail_counters[<tag>].count` by 1.
   - Append to `fail_counters[<tag>].occurrences[]`: `{ts, target, detail}` where `detail` is concrete — which command ran, which path was assumed, which action lacked a keep-list.
   - If the tag is new, create the entry, picking `threshold` by phase severity: load-bearing = 1, procedural = 2, cosmetic = 5.

4. **Persist captured suggestions.** Entries added to `improvement_suggestions[]` during this run — mid-run captures plus audit final-call entries — are written as part of the same `Write` call. The array is append-only.

4a. **Update `validation_freshness`.** This is the ONLY phase that writes to it:
   - If the block is missing, initialize it with the Phase 0 default shape.
   - Increment `validation_freshness.runs_since_validation` by 1.
   - Do NOT modify `last_validated_at`, `last_research_at`, `last_overlap_check_at`, `thresholds`, or `review_log[]` — those are user-owned. The skill never self-certifies freshness.

5. **Write the file** with the `Write` tool.

6. **Print run-end summary:**
   ```
   Run summary: outcome=<closed|paused|aborted>, FAIL tags=<count>, suggestions=<this-run-count> (total log: <all-time-count>)
   Tracker: <TRACKER_OUTPUT>   Baseline: <BASELINE_DIR>/<date>.json
   Review suggestions at: skills/machine-perf-audit/run_history.json → improvement_suggestions[]
   ```

7. **Threshold check** — for any counter where `count >= threshold`:
   - Print a **fix proposal** block: the failure pattern, the recommended SKILL.md edit (specific line + before/after drawn from `remediation_hint`), the tag.
   - **Apply automatically**: make the SKILL.md edit. The user reviews the change in their normal commit-review loop.
   - After applying: reset the counter to 0; set `applied_at`; optionally fill `applied_via`.
   - **Conflict handling**: if multiple tags trip in the same run, apply remediations serially (oldest tag first by `occurrences[0].ts`). Surface conflicts — never silently overwrite a remediation another tag just wrote.

---

## Edge cases

1. **Not Windows.** Phase 1 records the real platform and the skill runs only the lanes it has probes for. Lanes without a catalog are reported `unprobed (no <platform> probe catalog)` — never `clean`, and never with a guessed-equivalent command.
2. **No Docker / no WSL.** Phase 0.5 skips the `docker` and `io` lanes with the justification `component absent (Phase 1)`. The lanes appear in the ranking table as unprobed, not as zero-impact.
3. **Not elevated.** Tiers B and C are still produced — as instructions and as ticket requests. The skill never attempts to elevate and never suggests a workaround to elevation.
4. **No baseline snapshot.** Phase 2 records `baseline: none (first run)`; the delta section of the tracker says so explicitly rather than showing zeroes.
5. **A probe command is missing or fails.** Record `unknown` plus the verbatim error. Never infer a value from an adjacent signal.
6. **A protected agent is the top CPU consumer.** It stays in the report with its measured cost and goes to tier C as a scheduling/exclusion request. It never becomes a removal action, regardless of how large the number is.
7. **Corporate DLP blocks a path read.** Capture the access-denied output verbatim and mark the finding `partial — read blocked`. Do not retry with a different technique to get around it.
8. **The user asks the skill to run a cleanup command.** Decline the execution, point at the tracker row that contains the exact command, and let them run it. The read-only boundary is the skill's whole safety model.
9. **`REPO_ROOTS` is empty or none exist.** The orphan-venv and duplicate-wheel probes are skipped and recorded as skipped; the python lane still reports user-site, guard, sprawl and cache findings.

## Plugin skills composed by this skill

| Skill | Phase | Trigger |
|---|---|---|
| *(none — populate by hand if/when you discover compositions on first runs)* | — | — |

## Plugin skills NOT composed

- `quality-upgrade-advisor` — audits a **project's** dependency stack; this audits the **machine's** interpreter, venv and cache sprawl. Different subject, no shared probe.
- `safe-changes-impact-check` — models blast radius for **code** changes (schema, auth, orchestration); machine-action risk is modelled inline by Phase 7's tier + ordering constraints.
- `commit-ready` — the tracker is an artifact for the user to act on, not a repo change to commit. Committing it is the user's separate call.

## Out of scope

- **Applying any remediation.** There is no apply mode at v1. The skill emits the plan; the user executes it. This is the load-bearing boundary, not a convenience gap.
- **Background or scheduled monitoring.** Use `/loop` if a recurring check is wanted.
- **macOS / Linux probe parity.** v1 ships a Windows catalog. Other platforms are gated and reported honestly, not approximated.
- **Registry or service "tweaks" without evidence.** Every action traces to a measured cost in Phase 6.
- **Fleet or cross-machine comparison.** Baselines are per-machine and user-scoped.
- **Hardware recommendations.** The skill reports what the current hardware is doing, not what to buy.

## Usage

Tell Claude one of:

```
/machine-perf-audit
/machine-perf-audit python
/machine-perf-audit disk,docker
/machine-perf-audit delta
/machine-perf-audit everything crawls when docker is up
```

The skill walks Phases 1–10 and asks for explicit approval before advancing past every gate. Failure patterns accumulate in `run_history.json`; when a counter trips its threshold, the skill auto-edits its own SKILL.md per the `remediation_hint` and the user reviews the edit in their normal commit-review loop.

---

## Self-learning checklist (before shipping)

- [ ] `run_history.json` exists at the skill's root, initialized with the universal seed FAIL rules.
- [ ] The audit phase (`Phase 9`) lists one row per domain phase, with concrete evidence shapes.
- [ ] Every phase that consumes user input (Phases 3, 8) has a row format that records the input **verbatim**, never paraphrased.
- [ ] The terminal action requires the literal `tracker approved` — silence, "ok", "looks good" do NOT advance.
- [ ] At least one domain FAIL rule exists (seven do).
- [ ] Threshold tiers match phase severity: load-bearing=1, procedural=2, cosmetic=5.
- [ ] The ledger phase (`Phase 10`) is the last phase. No phase fires after it.
- [ ] `Phase 0.5 — Understand this run's expectations & build the run plan` is present, non-skippable, and precedes domain Phase 1.
- [ ] The audit phase walks the run plan: one row per executed step + one skip-justification row per skipped baseline step. `plan-silent-skip` and `plan-skipped-load-bearing-step-without-justification` are seeded in `run_history.json`.
- [ ] `Phase 0 — Freshness check` is present as the FIRST phase, before Phase 0.5, non-blocking, silent when fresh.
- [ ] `run_history.json` contains a `validation_freshness` block with thresholds runs=10, days=21.
- [ ] The ledger phase contains the `validation_freshness.runs_since_validation` increment step. The skill MUST NOT self-certify freshness.
- [ ] No probe in the SKILL.md mutates state. Grep the phase bodies for `prune`, `rm -rf`, `Remove-Item`, `rmi`, `uninstall` — every hit must be inside a *plan row the user runs*, never inside a phase's own probe block.
