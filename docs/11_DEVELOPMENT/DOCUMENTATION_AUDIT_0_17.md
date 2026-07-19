> Status: Maintained audit for ETLantic 0.17.0 publish-ready documentation cut.

# Critical Documentation Audit — ETLantic 0.17

This audit records the documentation condition after the publish-ready 0.17
remediation. It is a maintained release artifact, not a claim that every
historical or design page is part of the supported product. Reassess the open
items when release posture, supported deployment boundaries, or public package
behavior changes.

## Executive Summary

- **Overall documentation quality: Good (after remediation; was Fair).**
- **Would I personally trust this project based on the documentation?** Yes,
  for an evaluation or a documented single-tenant/reference deployment, after
  validating the selected plugins and operational controls against the
  capabilities and production-readiness guides. I would not infer broad
  enterprise-platform readiness from the Production/Stable classifier alone.
- **Why or why not?** The publish-ready cut now gives a credible path from
  installation through first execution, clearly identifies shipped packages,
  distinguishes execution from compilation, and states the bounded stable
  envelope. The docs are unusually explicit about deterministic plans, plugin
  trust, secrets, experimental Structured Streaming, and adopter-owned
  controls.   Trust is reduced by an incomplete diagnostic-code catalog and the large
  body of future design material that remains searchable beside shipped
  guidance. The bounded claim is defensible only if those limits remain
  prominent: stable for documented single-tenant/reference deployments;
  experimental remains experimental; multi-tenant isolation, deployment
  topology, compliance, SBOM/signing, and advanced supply-chain controls remain
  adopter-owned.

## High-Priority Issues

### 1. Impossible compatible-release installation range

- **Severity:** Critical
- **Location:** `docs/01_GETTING_STARTED/INSTALLATION.md`
- **Problem:** The installation guide previously recommended
  `etlantic>=0.16.0,<0.16`, an unsatisfiable range, and described it as accepting
  0.14 patches.
- **Impact:** A user following the recommended reproducible installation path
  could not install ETLantic and would reasonably conclude that the release was
  broken.
- **Recommended Fix:** Pin evaluation to `etlantic==0.17.0`; use
  `etlantic>=0.17.0,<0.18` only when compatible 0.17 patches are intentionally
  accepted.
- **Status:** Remediated in this docs cut

### 2. Wrong “What’s New” destination

- **Severity:** High
- **Location:** `docs/README.md` Green path
- **Problem:** “What’s new in 0.17” linked to `WHATS_NEW_0_16.md`.
- **Impact:** The first adopter-facing navigation step presented the wrong
  release delta and obscured the actual 0.17 capability graduation.
- **Recommended Fix:** Link directly to `WHATS_NEW_0_17.md` and keep the 0.17
  migration guide adjacent.
- **Status:** Remediated in this docs cut

### 3. Alpha language contradicts Production/Stable posture

- **Severity:** High
- **Location:** Root `README.md`, `docs/README.md`,
  `docs/10_REFERENCE/KNOWN_ISSUES.md`, `docs/10_REFERENCE/API_REFERENCE.md`,
  `docs/06_EXECUTION/LOCAL_PYTHON.md`, and
  `docs/11_DEVELOPMENT/SUPPORT.md`
- **Problem:** Release-facing pages stated bounded Production/Stable while
  deeper pages still described ETLantic or its support line as alpha.
  A 0.x API-compatibility warning is valid; calling the whole product alpha is
  not consistent with the selected classifier.
- **Impact:** Evaluators cannot tell whether the stable claim is deliberate,
  and support/API expectations become internally contradictory.
- **Recommended Fix:** Replace project-wide “alpha” wording with the bounded
  stable statement. Separately retain precise warnings that 0.x APIs may change
  between minor releases and support is best effort.
- **Status:** Remediated in this docs cut

### 4. Stale 0.16 tutorial and install pins

- **Severity:** High
- **Location:** Getting Started and execution tutorials; package installation
  examples
- **Problem:** Current-path pages retained 0.16 release labels or dependency
  pins after the 0.17 release.
- **Impact:** Users could install mixed core/plugin minors or believe the
  current tutorial targeted an older API.
- **Recommended Fix:** Pin runnable release examples to 0.17.0, reserve 0.16
  references for migration/history, and check current-path docs in CI.
- **Status:** Remediated in this docs cut

### 5. Prefect described as planned after shipping

- **Severity:** High
- **Location:** Getting Started, execution/orchestration guidance, package
  README, compatibility tables, and roadmap/status prose
- **Problem:** Some documentation treated Prefect as future even though
  `etlantic-prefect` ships an `ExecutionScheduler`.
- **Impact:** Users could overlook a shipped integration or mistake the local
  scheduler for a DAG compiler, deployment service, or Prefect Cloud feature.
- **Recommended Fix:** Describe the shipped feature consistently as an optional
  local direct-execution MVP; explicitly exclude deployment/serve, durable
  scheduling, and Cloud/server requirements.
- **Status:** Remediated in this docs cut

### 6. Status banner advertised stale capability state

- **Severity:** High
- **Location:** `docs/theme/javascripts/status-banner.js`
- **Problem:** The future-design banner said portable-relational support
  shipped only through 0.15 and advanced profiles remained planned.
- **Impact:** A global UI element overrode accurate page content with a stale
  capability claim and incorrectly marked some shipped Plugin SDK pages.
- **Recommended Fix:** Update the banner for 0.17 claims, exempt shipped SDK
  guides, and derive future status from maintained metadata where feasible.
- **Status:** Remediated in this docs cut

### 7. Package READMEs did not pin compatible releases

- **Severity:** High
- **Location:** `packages/*/README.md`
- **Problem:** Plugin install snippets used unpinned packages or did not show a
  compatible core/plugin pair.
- **Impact:** PyPI users could resolve mismatched plugin and core minors, then
  encounter entry-point or protocol incompatibilities.
- **Recommended Fix:** Show `==0.17.0` for reproducible evaluation and install
  matching core/plugin minors in every package README.
- **Status:** Remediated in this docs cut

### 8. CLI run example lost its in-memory seed

- **Severity:** High
- **Location:** Root `README.md`, Quickstart, First Pipeline, and
  Troubleshooting
- **Problem:** The documented in-memory seed existed only in one Python
  process, while a later `etlantic run` imported the pipeline in another
  process without that state.
- **Impact:** The flagship first-run command failed despite correct user
  copying, undermining confidence in the runtime.
- **Recommended Fix:** Execute the seeded example in one Python process, or use
  persistent file/callable storage for a separate CLI process; explain the
  process boundary.
- **Status:** Remediated in this docs cut

### 9. Design proposals competed with the Learn path

- **Severity:** High
- **Location:** Docs home, Examples, Plugin SDK, visualization/reference
  sections, and Development plans
- **Problem:** Detailed future designs appeared alongside runnable guides
  without a sufficiently strong current-product route.
- **Impact:** New users could copy unshipped APIs and mistake design depth for
  implementation status.
- **Recommended Fix:** Keep a short task-based Green path, label future pages
  visibly, move maintainer plans out of user learning sequences, and name
  Capabilities as the shipped-behavior authority.
- **Status:** Remediated in this docs cut

### 10. Diagnostic catalog is not complete enough for operations

- **Severity:** Medium
- **Location:** `docs/10_REFERENCE/DIAGNOSTICS.md`
- **Problem:** The page explains namespaces and selected PMXFORM codes but does
  not provide an exhaustive generated catalog of currently emitted codes,
  severity, trigger, and remediation. It also lists `PMXFORMxxx` twice.
- **Impact:** Operators and CI integrators cannot reliably map every diagnostic
  to a runbook or determine whether code changes are compatibility changes.
- **Recommended Fix:** Generate the catalog from code, include owner/severity/
  trigger/remediation/stability, remove duplicate namespace entries, and fail CI
  when emitted codes are undocumented.
- **Status:** Still open

### 11. Stable classifier could be read as an unbounded production claim

- **Severity:** High
- **Location:** Package metadata, README status blocks, evaluator and
  production-readiness guidance
- **Problem:** `Development Status :: 5 - Production/Stable` is necessarily
  terse, while the actual support claim is bounded.
- **Impact:** A reader who sees only package metadata may assume maintained
  multi-tenant isolation, deployment architecture, compliance evidence, SBOM
  and signing, or advanced supply-chain controls.
- **Recommended Fix:** Repeat the bounded envelope at release-facing decision
  points and preserve a direct capabilities/production-readiness link.
- **Status:** Accepted residual risk

### 12. Future-design classification depends partly on JavaScript path rules

- **Severity:** Medium
- **Location:** `docs/theme/javascripts/status-banner.js` and pages classified
  by path
- **Problem:** Status is inferred from allow/deny path lists rather than
  authoritative per-page metadata.
- **Impact:** New or renamed pages can silently receive the wrong status, and
  readers without JavaScript may miss the warning.
- **Recommended Fix:** Add source-level status metadata/admonitions and validate
  it in the docs consistency gate; keep the banner as a secondary aid.
- **Status:** Accepted residual risk

## Missing Documentation

Priority order:

1. **Bounded production support statement — added in this cut.** The README,
   docs home, evaluator path, capabilities, security, compatibility, and
   production-readiness material now constrain the stable claim.
2. **0.17 release delta and migration path — added in this cut.** The current
   guide links the correct What’s New and 0.16 → 0.17 migration pages.
3. **Reproducible 0.17 installation and plugin compatibility — added in this
   cut.** Core and package guides now prefer exact 0.17.0 pins.
4. **Task-based evaluator/Green path — added in this cut.** A first-time reader
   can move from status to installation, quickstart, capabilities, evaluator,
   and pilot guidance.
5. **Engine tutorials for supported reference paths — added or substantially
   remediated in this cut.** File storage, Polars, Pandas, SQL, PySpark, Airflow,
   and portable-transform routes are identified from the current guide.
6. **Prefect shipped-scope statement — added in this cut.** The docs distinguish
   local direct execution from deployment/serve and DAG compilation.
7. **Production profiles and production-readiness checklist — added or
   substantially remediated in this cut.**
8. **Complete generated diagnostic-code catalog — still missing.** Selected
   examples are not an operationally complete reference.
9. **Single source-level page-status inventory — still missing.** Status remains
   partly encoded in prose and JavaScript path rules.
10. **Supported deployment topology reference implementation/runbook — still
    missing by design.** This is adopter-owned under the 0.17 envelope; the docs
    should continue to say so rather than imply coverage.
11. **Multi-tenant isolation architecture and threat model — still missing by
    design.** Multi-tenancy is outside the bounded stable claim.
12. **Compliance mapping, release SBOM, artifact signing, provenance, and
    advanced supply-chain runbook — still missing/adopter-owned.**
13. **End-to-end incident and rollback runbooks for each optional engine —
    still missing.** Existing troubleshooting is useful but not a managed
    service operations manual.
14. **Versioned support/EOL matrix — still missing.** Migration and deprecation
    policy exist, but maintained-minor duration should be explicit.

## Documentation Improvements

The following text samples are recommended canonical wording.

**Installation range**

> For a reproducible evaluation, install `etlantic==0.17.0`. Use
> `etlantic>=0.17.0,<0.18` only when you intentionally accept compatible 0.17.x
> patches. Keep ETLantic core and optional plugin packages on the same minor
> release line.

**Project status**

> ETLantic 0.17.0 is production/stable for the documented single-tenant
> reference deployment. Public 0.x APIs may still change between minor
> releases, so pin versions and read the migration guide when upgrading.
> Structured Streaming and every surface explicitly labeled Experimental or
> Future design are outside the stable claim.

**Prefect status**

> `etlantic-prefect` ships an optional Prefect-backed
> `ExecutionScheduler` for local direct execution of resolved ETLantic plans.
> It is not a DAG compiler and does not claim Prefect deployment/serve, durable
> scheduling, or a managed Prefect Cloud topology.

**Bounded stable envelope**

> The stable envelope covers documented single-tenant/reference deployments
> using shipped capabilities and required production controls. Multi-tenant
> isolation, deployment topology, compliance evidence, SBOM/signing, and
> advanced supply-chain controls remain the adopter’s responsibility. Do not
> treat the package classifier as evidence that those controls are provided.

## Navigation Improvements

Keep the documentation task-based at the top level and progressively disclose
the architecture:

1. **Evaluate:** Project status → Capabilities → Known limitations → Evaluator
   brief → Production readiness.
2. **Start:** Installation → Quickstart → First pipeline → Troubleshooting.
3. **Choose an execution path:** Local/files → Polars/Pandas → SQL → PySpark →
   Airflow compile → Prefect local scheduling.
4. **Build:** Contracts → Transformations → Pipelines → Profiles → execution
   operations.
5. **Integrate:** Public API → CLI → configuration → compatibility →
   diagnostics → Plugin SDK.
6. **Operate:** Production profiles → security → secrets → reliability →
   observability → upgrade/rollback.
7. **Contribute and design:** Contributor essentials → decisions → roadmap →
   clearly separated maintainer plans and future proposals.

The current Green path is the right entry point. Keep Capabilities as the
authority for shipped behavior, avoid linking design proposals from beginner
sequences, and put a visible source-level status on every partial,
experimental, future, normative, or internal page. Historical release material
should remain reachable through migrations and changelog navigation rather
than competing with the current guide.

## New User Experience Review

Historically, a first-time visitor encountered a polished concept and broad
architecture, but then hit contradictory evidence: an impossible package
range, a 0.17 link that opened 0.16 notes, alpha language beside stable
metadata, stale 0.16 tutorial pins, “planned” wording for shipped Prefect
support, and an in-memory CLI run that could not inherit its seed. Rich future
design pages looked as actionable as current guides. These are credibility
failures, not cosmetic defects, because they occur before or during first
success.

After this cut, the preferred journey is coherent:

1. The visitor sees the bounded production/stable statement and adopter-owned
   exclusions.
2. The Green path leads to the actual 0.17 delta.
3. Installation gives a satisfiable exact pin and compatible plugin versions.
4. Quickstart/First Pipeline produces a same-process seeded success.
5. Capabilities separates shipped, experimental, and future behavior.
6. Task links route the user to a specific engine tutorial.
7. Evaluator and production-readiness pages frame a controlled pilot rather
   than implying universal deployment readiness.

Remaining confusion is concentrated deeper in the site. Search results can
still land on future design pages; status classification is partly
UI/path-driven; Prefect “local MVP” may be overread as production deployment
support; and diagnostics do not yet form a complete operator catalog. The
project is trustworthy for its stated bounded use only when the reader follows
the current authority chain, not when any single historical or design page is
read in isolation.

## Adoption Readiness Score

Scores are documentation readiness on a 1–10 scale, not product capability
scores.

| Category | Before remediation | After this cut | Notes |
|---|---:|---:|---|
| Clarity | 5 | 8 | Bounded status and shipped/future distinctions are much clearer. |
| Completeness | 6 | 8 | Core user and evaluator paths are covered; enterprise topology, compliance, and full diagnostics remain outside or incomplete. |
| Discoverability | 5 | 8 | Green path and task links materially improve routing; deep design pages still compete in search. |
| Learnability | 6 | 8 | First success is now plausible and engine tutorials are surfaced. |
| API Documentation | 6 | 8 | Public surfaces and compatibility are documented; exhaustive diagnostics remain incomplete. |
| Examples | 6 | 8 | Pins, process boundaries, and current package examples are substantially corrected. |
| Contributor Experience | 7 | 8 | Development index, release process, status conventions, and checks are strong. |
| Professionalism | 5 | 9 | Release truth, classifiers, and support pages now agree on the bounded stable claim. |

**Overall:** approximately **5.8/10 before remediation** and **8.1/10 after
this cut**. The post-cut score assumes the bounded stable claim remains visible
and is not interpreted as managed-platform or compliance readiness.

## Prioritized Action Plan

Exact completion order:

1. **[Done]** Replace the impossible install range with `==0.17.0` and
   `>=0.17.0,<0.18`.
2. **[Done]** Correct the Green-path What’s New link to 0.17.
3. **[Done]** State the bounded Production/Stable envelope on release-facing
   pages.
4. **[Done]** Update the current-version guide and release-truth language to
   published 0.17.0.
5. **[Done]** Update current tutorials and install examples from 0.16 to 0.17.
6. **[Done]** Pin core/plugin combinations in package READMEs.
7. **[Done]** Correct Prefect from “planned” to shipped local direct-execution
   MVP, with explicit exclusions.
8. **[Done]** Repair the seeded in-memory first-run flow and explain process
   isolation.
9. **[Done]** Update the global status banner for shipped 0.17 capabilities and
   SDK pages.
10. **[Done]** Establish the task-based Green path and identify Capabilities as
    the shipped-behavior authority.
11. **[Done]** Separate maintainer plans/design proposals from the primary
    learning path and label future material.
12. **[Done]** Surface engine-specific tutorials, evaluator guidance,
    production profiles, and pilot readiness.
13. **[Done]** Reconcile every project-wide “alpha” statement with bounded
    stable posture while preserving 0.x API and best-effort support warnings.
14. **[Remaining]** Generate an exhaustive diagnostics catalog from code and
    enforce documentation coverage in CI.
15. **[Remaining]** Move page status to source metadata/admonitions and validate
    every non-current page in the docs check.
16. **[Remaining]** Add a versioned support/EOL matrix for core and plugins.
17. **[Remaining]** Add tested upgrade and rollback smoke procedures for the
    reference deployment.
18. **[Remaining]** Add per-engine incident/troubleshooting runbooks, starting
    with SQL, PySpark, Airflow, and Prefect local execution.
19. **[Remaining]** Add an explicit adopter-control checklist for deployment
    topology, multi-tenancy, compliance, SBOM/signing, provenance, and advanced
    supply chain without implying that ETLantic supplies those controls.
20. **[Remaining]** Make this audit a release-gate artifact: revisit scores,
    statuses, links, pins, banner rules, and open residual risks for every
    publish-ready documentation cut.
