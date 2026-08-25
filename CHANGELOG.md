# SENTINEL Changelog

## Version 0.15.0-rc.2 — Reporting, Accessibility, and Scale Hardening

**Date:** August 25, 2026  
**Project schema:** 14

### Reporting

- Corrected the Letter-size cover geometry that could create a blank second page.
- Added print cohesion rules for headings, paragraphs, table headers, rows, and long cell values.
- Replaced the fixed-footer page counter that rendered as `Page 0` with Cascading Style Sheets paged-media margin boxes and reliable `Page X of Y` numbering on the validated Chromium print engine.
- Verified a representative 14-page Letter report with Executive Summary on page 2, no accidental blank pages, and correct numbering from Page 1 of 14 through Page 14 of 14.
- Regenerated nested custom-section and evidence-selection identifiers when creating a new report revision, eliminating duplicate UUID collisions while preserving report content, ordering, relationships, and revision provenance.

### Accessibility and interaction

- Added programmatic label associations for generated select fields and audited filters.
- Strengthened command-palette dialog semantics, hidden-state reporting, focus containment, Escape behavior, and focus restoration.
- Added forward and reverse focus wrapping to record modals with trigger-focus restoration.
- Increased checkbox and radio geometry and provided 44-pixel mobile label targets.
- Added reduced-motion handling for nonessential animation and transition behavior.

### Performance and scale

- Added a 500-row interactive rendering limit with visible disclosure for large registers.
- Applied the guardrail to generic registers, the Evidence Vault, Timeline, Coverage Matrix, and Relationship Gap Queue.
- Preserved all underlying records for exports, reports, persistence, packages, and analysis.
- Added a large-project profile and warning above 5,000 material records.
- Added focused tests proving 600 records remain stored while 500 render and that the large-project state activates at the configured threshold.

### Validation and release integrity

- Added 24 Release Candidate 2 static hardening assertions.
- Added 21 browser, accessibility, scale, and Portable Document Format assertions.
- Passed 288 focused assertions across nine suites.
- Added the representative Letter PDF, rendered contact sheet, preflight record, and final acceptance checklist.
- Kept Project Schema 14 unchanged and retained migration from Schemas 1 through 13.

## Version 0.15.0-rc.1 — Professional Report Builder 2.0 and Release-Candidate Reconciliation

**Release date:** August 24, 2026  
**Project schema:** 14  
**Release type:** Release Candidate

### Corrected release integrity

- Superseded the earlier archive labeled Version 0.14.0 after final review showed its application source remained Version 0.13.5 / Project Schema 13.
- Reconciled application identity, project schema, storage key, migration fixtures, documentation, validation records, tests, release status, and manifest.
- Removed stale validation claims, backup source files, cache files, and failed development artifacts from the canonical release.

### Added Professional Report Builder 2.0

- Added a persistent project-level report artifact with multiple governed revisions.
- Added ordered built-in sections and analyst-created custom sections.
- Added dedicated Executive Summary, Scope and Authorization, Methodology, Site Overview, Security Architecture, Assessment Limitations, and Conclusion records.
- Added client branding, logo, sensitivity marking, handling instructions, header, footer, prepared-by, reviewer, approval, and issuing-authority controls.
- Added explicit evidence selection, report-specific captions, section placement, finding association, and display order.
- Added full selectable appendices for tests, observations, evidence, Photo Log, coverage, Rules of Engagement, Daily Field Logs, remediation, retests, baselines, Control Chains, assumptions, issues, interactions, and outstanding questions.
- Added standalone Hypertext Markup Language, Markdown, structured JavaScript Object Notation, print-to-Portable Document Format, and controlled report-package outputs.
- Added report-package manifests and explicit selected-evidence boundaries.

### Added report governance

- Added the lifecycle Draft → In Review → Approved → Final Issue.
- Added reviewer, approval authority, issuing authority, rationale, timestamp, and history records.
- Added atomic Final Issue so failed validation or hashing cannot leave a partially issued report.
- Added Secure Hash Algorithm 256-bit sealing of the issued snapshot.
- Added read-only Final Issue revisions.
- Added material live-project divergence detection without modifying the sealed issue.
- Added new Draft revisions linked to the prior issue.

### Fixed

- Fixed a report-renderer syntax defect found before integration.
- Fixed Final Issue metadata entry invalidating the approval fingerprint before issuance.
- Fixed Final Issue transaction behavior so issue metadata, snapshot, seal, and lock commit together.
- Fixed custom-section preservation through report normalization.
- Fixed issued reports appearing current after material project changes.
- Added an end-to-end selected-evidence test that proves unrelated evidence remains outside report output and the report package.

### Validation

- 31 full-application static assertions passed.
- 50 migration and export assertions passed.
- 29 report static assertions passed.
- 43 report-governance semantic assertions passed.
- 59 Professional Report Builder browser assertions passed.
- 23 broad release-candidate browser smoke assertions passed.
- 8 controlled report-package inspection assertions passed.
- 243 executed assertions passed across seven suites.
- The managed validation environment prevented the complete secure-origin inherited browser suite from running; that limitation is documented and is not represented as a pass.

### Known remaining release-candidate work

- Unrestricted secure-origin inherited browser acceptance
- Firefox, Safari, and WebKit acceptance
- Physical-device media-capture acceptance
- Storage and recovery fault injection
- Accessibility review
- Performance profiling
- Independent security review
- Representative final Portable Document Format issue review

## Version 0.13.5 — Interface Consolidation and Workflow Cleanup

**Release date:** August 24, 2026
**Project schema:** 13
**Release type:** Cross-module user-interface and user-experience hardening

### Added

- Added workflow-centered navigation groups for Workspace, Fieldwork, Analysis, Closeout, and Administration.
- Added a consolidated Project menu for New, Open, Save, Save As Copy, plain export, encrypted export, Emergency Export, Import, checkpoints, and recovery.
- Added one clear Project files and backups entry to the sidebar.
- Added collapsible and resizable desktop navigation and Traceability Inspector panels.
- Added device-local persistence for panel visibility and widths without changing project data or Project Schema 13.
- Added record-count and attention badges to high-value navigation destinations.
- Added sticky contextual view headers with module context, purpose, and primary actions.
- Added Dashboard lifecycle guidance for SCOPE → PLAN → RECON → TEST → OBSERVE → EVIDENCE → FINDINGS → REPORT → RETEST.
- Added state-aware next-action guidance and high-frequency record shortcuts to the Dashboard.
- Added a skip link, stronger focus treatment, current-page semantics, expanded-state reporting, and explicit drawer close controls.
- Added `test_ui_cleanup.py` with 32 desktop and mobile shell assertions.
- Added static validation for the streamlined shell, workflow navigation, responsive grid, and Dashboard guidance.

### Changed

- Reorganized Advanced Mode from 21 equal-weight destinations into five operational groups.
- Kept Easy Mode focused on the essential project, map, test, observation, evidence, finding, and report workflow.
- Changed the Traceability Inspector from an always-visible third column to an on-demand panel.
- Changed selected-record behavior so the Inspector opens automatically on wide screens but remains an explicit drawer on small screens.
- Changed view transitions to reset the main scroll position.
- Reduced card shadow intensity, improved empty states, and simplified the visual hierarchy of the shell.
- Made classification and storage status more compact while keeping handling information persistently visible.
- Made the footer single-line and compact on mobile.
- Updated Save As Copy and project-package regression tests to exercise the consolidated Project menu.

### Fixed

- Fixed the application grid so the classification banner, workspace, and footer occupy independent rows.
- Fixed a desktop grid auto-placement defect that could reduce the main workspace to nearly zero width after collapsing the sidebar.
- Fixed the Search button so clicking its nested label no longer immediately closes the command palette.
- Fixed mobile record selection so an empty Inspector backdrop does not block navigation after closing a workbench.
- Fixed breakpoint behavior that could display a mobile menu button on desktop.
- Fixed mobile footer wrapping and page-level horizontal overflow in the cleaned shell.
- Fixed mobile navigation backdrop acceptance tests so they target the area outside the drawer.

### Validation

- 31 static assertions passed.
- 504 browser assertions passed across 21 isolated suites.
- 535 total assertions passed against the canonical Version 0.13.5 source.
- All 12 historical schema fixtures migrated to Project Schema 13 and passed post-migration audit.
- JavaScript syntax, declared-function uniqueness, static element identifiers, package round trips, encrypted storage, direct capture, evidence workflows, Assessment Assurance, Control Chains, remediation, retesting, baselines, reports, and mobile Evidence behavior were revalidated.

### Known limitations

- Automated browser acceptance remains Chromium-focused.
- Firefox, Safari, WebKit, screen-reader, and physical-device acceptance remain roadmap items.
- The complete Professional Report Builder 2.0 remains scheduled for the next major development series.
- Interface preference persistence is device-local and is intentionally not included in project packages.

## Version 0.13.0 — Baseline Comparison and Regression Analysis

**Release date:** August 24, 2026
**Project schema:** 13
**Development batch:** 11

### Immutable baseline records

- Replaced count-oriented baseline snapshots with complete normalized assessment snapshots.
- Added deterministic Secure Hash Algorithm 256-bit (SHA-256) sealing for baseline material.
- Added seal metadata, verification history, integrity results, source schema, source application version, and source project timestamp.
- Added explicit `ACTIVE` and `RETIRED` baseline states.
- Replaced destructive baseline deletion with retirement and rationale.
- Added baseline integrity verification before comparison review sign-off.
- Added import, recovery, and migration handling that seals eligible legacy baselines before use.

### Semantic comparison engine

- Added baseline-to-baseline and baseline-to-current-project comparison.
- Added field-level comparison across project scope, authorization, assurance, hierarchy, controls, tests, events, observations, evidence, findings, positive observations, interactions, assumptions, issues, Daily Field Logs, field notes, remediation submissions, formal retests, Control Chains, and map records.
- Added record matching by stable Universally Unique Identifier (UUID) with persistent human-readable identifier fallback.
- Added change types for `ADDED`, `MODIFIED`, `DELETED`, and `ABSENT_LATER`.
- Added record tombstones to preserve supported deletion rationale, actor, timestamp, record identity, and record category.
- Preserved unexplained absence as a separate review condition rather than assuming deletion.
- Expanded material-field coverage for evidence integrity, finding severity and remediation, test results, authorization, control conditions, retest state, Control Chains, and map geometry.

### Regression and improvement analysis

- Added automatic analytical impact suggestions:
  - `REGRESSION`
  - `IMPROVEMENT`
  - `REVIEW`
  - `NEUTRAL`
- Added direction-aware classification for finding severity, test result, evidence integrity, remediation progress, retest state, assurance state, and coverage metrics.
- Added separate automatic reason and final analyst disposition.
- Prevented automatic classifications from becoming signed conclusions without analyst review.

### Coverage deltas

- Added comparable Assessment Assurance metrics for each endpoint.
- Added planned, attempted, completed, and evidenced test deltas.
- Added control and location coverage deltas.
- Added open-blocking-gap and accepted-limitation deltas.
- Added direction-aware presentation for metrics where lower values are favorable.

### Comparison review and integrity

- Added first-class baseline comparison records with UUIDs and human-readable codes.
- Added per-change classification, status, rationale, owner, reviewer, and review timestamp.
- Added an overall analyst comparison conclusion.
- Added review gates requiring a disposition, rationale, and owner for every regression and review item.
- Added endpoint integrity checks before sign-off.
- Added SHA-256 comparison review values and fast staleness fingerprints.
- Added automatic invalidation when comparison material, dispositions, or endpoint hashes change.
- Added review history and current, Draft, and stale states.
- Added cryptographic review verification to the test interface and release suite.

### Baselines and Regression Analysis workspace

- Added coordinated **Compare**, **Snapshots**, and **Review Log** views.
- Added endpoint selectors, summary cards, category cards, and coverage-delta cards.
- Added category, impact, change-type, and free-text filters.
- Added a detailed material-change register with before and after values.
- Added individual change-review dialogs and comparison-sign-off workflow.
- Added baseline verification, JavaScript Object Notation (JSON) export, retirement, restoration, and compare-to-current actions.
- Added reviewed comparison reopening and staleness visibility.

### Search, navigation, reports, and exports

- Added baseline comparisons to global search, record navigation, and the command palette.
- Added JSON comparison export.
- Added Comma-Separated Values (CSV) material-change register export.
- Added standalone Hypertext Markup Language (HTML) comparison export.
- Added reviewed comparison sections to interactive, standalone HTML, Markdown, and print-to-Portable Document Format (PDF) assessment reports.
- Added reviewed comparison state to report-readiness analysis.
- Added baseline comparisons and tombstones to project audit, copy/remap, persistence, recovery, and package workflows.

### Compatibility and validation

- Added Schema 12 → Schema 13 migration.
- Added a historical Schema 12 fixture derived from Version 0.12.0.
- Preserved migration from Schemas 1 through 12.
- Added a dedicated 35-assertion baseline regression suite.
- Expanded static validation for immutable baselines, semantic comparison, review workflow, reporting, and exports.
- Final release validation passed 499 assertions: 27 static assertions and 472 browser assertions across 20 isolated browser suites.

### Known limitations

- Automatic impact suggestions are heuristic and require professional analyst review.
- Stable UUIDs provide the strongest historical match; manually rewritten identifiers can require reconciliation.
- Tombstones explain only deletions captured by supported deletion workflows.
- Baselines preserve evidence metadata, relationships, and hashes rather than duplicating every evidence binary into every snapshot.
- Comparison review hashes provide project-model tamper evidence, not legally qualified digital signatures.

## Version 0.12.0 — Remediation and Formal Retesting

**Project schema:** 12
**Release:** Batch 10

### Added

- First-class remediation-submission records separate from findings
- Immutable source-finding and recommendation snapshots
- Remediation owner, implementation date, requested retest date, implementation evidence, compensating controls, notes, and lifecycle history
- Separate remediation acceptance workflow with reviewer, timestamp, attestation, and rationale
- Superseding submissions for correction without rewriting historical records
- First-class formal retest records with immutable source-finding and remediation snapshots
- Draft, Planned, Authorized, In Progress, Completed, Reviewed, and Cancelled retest lifecycle
- Retest objective, scope, authorization, restrictions, safety controls, method, expected behavior, criteria, execution period, evidence, result, and analyst notes
- Retest sequence numbers and corrective or follow-up relationships
- Completion Secure Hash Algorithm 256-bit fingerprint
- Independent review with tester/reviewer separation, decision, rationale, review history, and review SHA-256 value
- Remediated, Partially Remediated, Not Remediated, Unable to Verify, and Pending results
- Compensating-control verification
- Four-view Remediation & Formal Retesting workspace: queue, submissions, register, and independent review
- Recommendation-to-remediation-to-retest Traceability Graph relationships
- Remediation and formal-retest sections in standalone Hypertext Markup Language and Markdown reports
- Baseline-level added, removed, and materially changed remediation and retest comparison
- Schema 11 historical migration fixture
- Dedicated `test_remediation_retesting.py` browser acceptance suite

### Changed

- Project Schema 11 projects migrate to Project Schema 12.
- Submitted remediation records are read-only; corrections create superseding submissions.
- Authorized retest plans are immutable.
- Completed and reviewed retests are immutable; corrections create linked follow-up records.
- Final report readiness now blocks completed but unreviewed retests.
- Final report readiness now blocks verified finding closure without an approved Remediated retest.
- Reviewed retests update finding closure, remediation status, and retest history without altering the original finding narrative or evidence.
- Traceability exports now include finding, remediation, evidence, control, and retest relationships.
- Baseline snapshots and comparisons now include remediation submissions and retests.
- The complete repeatable validation set now covers 23 static and 434 browser assertions.

### Fixed

- The previous placeholder `retests` collection is now governed by a complete operational workflow.
- Source finding and remediation context can no longer silently change after a submission or retest is created.
- Completed execution records can no longer be edited while awaiting review.
- A failed or returned review no longer requires changing the completed record; a corrective retest preserves both histories.
- Closed findings now require a recorded rationale before reopening for additional retesting.
- Imported Schema 11 records are normalized with conservative immutable snapshots and legacy acceptance or completion metadata.
- Imported-project audit now evaluates remediation-submission workflow rules against the imported project rather than the currently active project.
- Retest authorization expiration and execution timestamp order are validated.
- Loose source, packaged source, schema, tests, documentation, and release identity are reconciled for Version 0.12.0.

### Validation

- 434 browser assertions passed across 19 isolated browser suites.
- 23 static assertions passed.
- 457 total assertions passed.
- Migration and post-migration audit passed for Schemas 1 through 11.
- Real-origin acceptance reconfirmed IndexedDB, Web Cryptography, encrypted storage and packages, capture recovery, direct media, evidence integrity, field operations, Assessment Assurance, Control Chains, mapping, reports, and mobile layouts.

### Known limitations

- Completion and review fingerprints are tamper-evidence inside the project model, not legally qualified digital signatures.
- SENTINEL cannot determine whether a remediation or retest conclusion is substantively correct; professional review is required.
- Automated browser acceptance currently covers Chromium; Firefox, Safari, WebKit, and physical target devices still require acceptance.
- The cryptographic implementation has not undergone an independent external review.
- Full semantic comparison between arbitrary baselines and the complete visual report composer remain future roadmap work.

## Version 0.11.0 — Control Chains and Defense in Depth

**Project schema:** 11
**Release:** Batch 9

### Added

- First-class Control Chain records with persistent identifiers, protected-asset relationships, report settings, confidence, conclusions, consequence narratives, and lifecycle history
- Ordered expected and observed protection paths referencing locations, controls, tests, observations, evidence, findings, and positive observations
- Per-step defense layer, state, evidence, finding, and analyst-note fields
- Sequence-aware expected-versus-observed comparison using longest-common-subsequence analysis
- Eight-layer defense-in-depth model covering Property Boundary through Protected Assets
- Worked, Partially Worked, Failed, Not Tested, and Insufficient Evidence states
- Evidence-aware state suggestions for defense layers
- Dedicated Control Chains workspace with Compare, Expected, Observed, Layers, Combined, and Portfolio views
- Relationship-only visual path diagrams and defense-layer stacks
- Combined-control interaction candidates for multiple documented degraded controls
- Separate evidence-limitation candidates that are never treated as control failures
- Draft, Validated, Reported, and Archived lifecycle with reviewer attribution and transition rationale
- Material-change reopening and Assessment Assurance sign-off staleness
- Per-chain JSON, portfolio JSON, path Scalable Vector Graphics (SVG), and defense-layer SVG exports
- Map marker links to Control Chain records and chain-aware map highlighting
- Control Chain participation in global search, command palette, Traceability Inspector, and visual Traceability Graph
- Control Chain preservation in baselines and added, removed, and changed baseline comparison
- Control Chain sections and print-legible diagrams in interactive, standalone HTML, Markdown, and browser-PDF reports
- Schema 10 historical migration fixture
- Dedicated `test_control_chains.py` browser acceptance suite

### Changed

- Project Schema 10 projects migrate to Project Schema 11.
- Report-readiness analysis now evaluates reportable Control Chains and their lifecycle state.
- Assessment Assurance material-state fingerprints now include Control Chain content.
- Traceability exports now include chain relationships and ordered path edges.
- Map marker record types now include `CHAIN`.
- Baseline snapshots preserve Control Chains, defense layers, review history, and path relationships.
- Exported SVG diagrams use a white background and dark labels for report and print legibility.
- The complete repeatable validation set now covers 20 static and 394 browser assertions.

### Fixed

- Expected-versus-observed comparison now preserves sequence, duplicates, and reordered relationships instead of reducing paths to unordered sets.
- Insufficient evidence is no longer counted as a failed or degraded control in combined-control analysis.
- Validation now requires the expected path to connect the documented entry location to the protected Asset record.
- Validated and reported Control Chains cannot silently retain review status after a material edit.
- Report diagrams no longer inherit dark-interface colors that become unreadable on white output.
- Unique SVG marker identifiers prevent arrowhead collisions when multiple diagrams appear in one report.
- The Plan Settings delete-button handler is now bound only after its modal exists, eliminating an inherited map-workspace runtime error.
- Canonical source, schema, tests, fixtures, documentation, manifest policy, and release identity are reconciled for Version 0.11.0.

### Validation

- 394 browser assertions passed across 18 isolated browser suites.
- 20 static assertions passed.
- 414 total assertions passed.
- Migration and post-migration audit passed for Schemas 1 through 10.
- Real-origin acceptance reconfirmed IndexedDB, Web Cryptography, encrypted storage and packages, capture recovery, direct media, evidence integrity, field operations, Assessment Assurance, traceability, mapping, reports, mobile layouts, and every new Control Chain workflow.

### Known limitations

- Control interaction and evidence-limitation candidates are analytical prompts, not independent proof of exploitability, likelihood, or consequence.
- The visual editor models defensive relationships and does not generate instructions for bypassing safeguards.
- Automated browser acceptance currently covers Chromium; Firefox, Safari, WebKit, and physical target devices still require acceptance.
- The cryptographic implementation has not undergone an independent external review.
- Formal remediation and multi-retest workflow, full semantic baseline comparison, and the complete report composer remain future roadmap work.

## Version 0.10.0 — Secure Field Capture and Data Protection

**Project schema:** 10
**Release:** Batch 7, completed after Batch 8

### Added

- Direct still-photograph capture from a local camera preview
- Direct video capture with live preview, recording indicator, elapsed status, and configured maximum duration
- Direct audio-note capture with recording indicator, elapsed status, and configured maximum duration
- Camera-facing preference and browser file-selection fallback
- Authorization acknowledgement tied to project photography and recording restrictions
- Recoverable Pending Field Captures queue
- Project-scoped queue persistence across reload and workspace lock
- Automatic active-test and location linking for captures
- Immutable capture commit with SHA-256 hashing, acquisition metadata, verification history, custody history, and timeline events
- Optional encrypted local project storage
- Advanced Encryption Standard in Galois/Counter Mode (AES-GCM) authenticated encryption for project records, evidence binaries, map assets, checkpoints, and pending captures
- Random project data key wrapped by a Password-Based Key Derivation Function 2 with Secure Hash Algorithm 256-bit (PBKDF2-SHA-256) passphrase-derived key using 250,000 iterations
- Project-specific workspace locking
- Inactivity lock and hidden-tab lock options
- Protected-preview behavior while the document is hidden
- Passphrase rotation through data-key rewrapping
- Safe restoration from encrypted storage to ordinary IndexedDB while retaining the screen lock
- Encrypted `.sentinel.enc` portable packages
- Full-envelope metadata confidentiality and authenticated package import
- Export-authorization acknowledgement
- Emergency encrypted export with metadata-only recovery fallback
- Persistent classification and handling banner
- Browser storage estimate, quota percentage, persistence state, and persistent-storage request
- Storage-pressure warning and backup-readiness state
- Security & Storage workspace
- Historical Schema 9 migration fixture
- Dedicated secure-storage, encrypted-package, capture-recovery, direct-media, and security-interface regression suites

### Changed

- Project Schema 9 projects migrate to Project Schema 10.
- Protected projects no longer retain a plaintext local recovery shadow.
- The Project Library uses a user-controlled non-sensitive label for protected projects.
- Portable-package imports intentionally reset destination-device lock and encryption flags.
- Security and capture commands are available from the command palette.
- Evidence and Field workspaces expose direct photo, video, and audio actions.
- The repeatable validation set now covers 17 static and 348 browser assertions.

### Fixed

- Direct captures are removed from the staging queue only after the evidence binary, metadata, relationships, timeline event, project validation, and save complete successfully.
- Locking now stops open media streams and stages an active recorder when the browser can finish it cleanly.
- Wrong local-storage and package passphrases fail authenticated decryption instead of returning partial data.
- Passphrase rotation after a locked browser reload now preserves access to existing encrypted binaries.
- Local decryption restores every project-scoped protected store and removes stale protected copies.
- Canonical source, documentation, tests, schema, manifest policy, and release identity are reconciled for Version 0.10.0.

### Validation

- 348 browser assertions passed.
- 17 static assertions passed.
- 365 total assertions passed.
- Migration and post-migration audit passed for Schemas 1 through 9.
- Real-origin acceptance covered direct camera, video, and audio capture with deterministic Chromium fake devices; encrypted capture recovery; every protected local store; wrong and correct passphrases; passphrase rotation; encrypted package download and clean-profile import; inherited field, evidence, assurance, reporting, migration, and mobile workflows.

### Known limitations

- Passphrases cannot be recovered.
- Automated direct-media acceptance uses Chromium fake media devices; physical-device acceptance remains required.
- Automated browser acceptance currently covers Chromium only.
- Encryption and packaging operate in browser memory and remain subject to device memory and quota constraints.
- Screen locking alone does not encrypt browser storage.
- Logical deletion cannot guarantee secure erasure.
- The cryptographic implementation has not undergone an independent external review.

## Version 0.9.0 — Assessment Assurance and Traceability 2.0

**Project schema:** 9
**Release:** Batch 8

### Added

- Dedicated Assessment Assurance workspace
- Coverage Matrix, Relationship Gap Queue, and Completeness and Sign-off panels
- Six explicit coverage outcomes: Not Tested, Tested — No Evidence, Inconclusive, Control Passed, Control Failed, and Not Applicable
- Independent evidence-sufficiency states: Sufficient, Review, Insufficient, and Not Assessed
- Coverage analysis by control, test, hierarchy location, security domain, control type, and assessment day
- Planned, attempted, completed, evidenced, and assured coverage summaries
- Hierarchy aggregation that includes descendant locations
- Automated relationship-gap detection for untested controls, unlinked tests, missing locations, unsupported conclusions, unrelated evidence, evidence-integrity failures, and unassessed zones or assets
- Change-controlled gap dispositions with Open, Acknowledged, and Accepted states
- Accepted-limitation disclosure in interactive, standalone Hypertext Markup Language, and Markdown reports
- Accountable-owner requirement for accepted limitations
- Acceptance restrictions for evidence-integrity failures and unsupported report conclusions
- Assessment-completeness checklist with Pass, Review, and Block states
- Analyst assurance sign-off with material-state fingerprint, Secure Hash Algorithm 256-bit value, history, revocation, and automatic staleness detection
- Report-readiness enforcement for assurance gaps, sampling documentation, and assurance sign-off
- Coverage JavaScript Object Notation and Comma-Separated Values exports
- Visual directional Traceability Graph
- Upstream, downstream, and combined traversal
- Configurable graph depth and node limits
- JavaScript Object Notation, Comma-Separated Values, and Scalable Vector Graphics graph exports
- Assessment-assurance disclosure in standalone Hypertext Markup Language and Markdown reports
- Historical Schema 8 migration fixture
- Dedicated 64-assertion Assessment Assurance regression suite

### Changed

- Project Schema 8 projects migrate to Project Schema 9.
- Advanced navigation now presents Coverage as the Assessment Assurance workspace.
- Coverage outcomes and evidence sufficiency are calculated separately.
- Final report actions require a current assurance sign-off.
- Accepted limitations remain visible in assurance summaries and report warnings.
- Traceability now covers locations, controls, tests, events, observations, evidence, findings, positive observations, interactions, field notes, assumptions, issues, questions, and retests.
- New baseline snapshots preserve assurance records, daily logs, questions, and retests.
- The repeatable runner now includes the assurance suite and supports configurable parallel jobs and per-suite timeouts.

### Fixed

- Baseline snapshots no longer omit the Assessment Assurance record.
- Baseline snapshots no longer omit Daily Field Logs, outstanding questions, or retest collections.
- Assurance fingerprints now preserve structured evidence-custody history consistently.
- Duplicate and incomplete scratch integrations were removed before packaging; one canonical source is retained.
- Source, schema, tests, documentation, manifest, and package identity are reconciled for Version 0.9.0.

### Validation

- 270 browser assertions passed.
- 12 static assertions passed.
- 282 total assertions passed.
- Migration and post-migration audit passed for Schemas 1 through 8.
- Chromium acceptance covered multidimensional coverage, gap rules, sign-off and staleness, graph traversal and exports, report integration, baseline preservation, evidence persistence, field workflows, package round-trip, historical migrations, and mobile layouts.

### Known limitations

- Secure Field Capture and Data Protection work remains deferred.
- Local browser storage and `.sentinel` packages are not encrypted.
- Direct camera, microphone, and video capture is not implemented.
- Automated browser acceptance currently covers Chromium only.

## Version 0.7.0 — Evidence Workstation

**Project schema:** 8
**Release:** Batch 6 plus stabilization gate

### Added

- Evidence Vault and Photo Log workspaces
- Search, filtering, grouping, bulk evidence operations, and thumbnails
- Image, audio, video, text, and Portable Document Format preview
- Acquisition metadata, verification history, chain of custody, current custodian, and metadata history
- Non-destructive image annotation, measurement, crop, rotation, redaction, and blur
- Derived Portable Network Graphics evidence with new identifiers and hashes
- Original-to-derived comparison
- Standalone Hypertext Markup Language Photo Log export
- Report-selected image embedding
- Project-package Format 3
- Repeatable static and browser acceptance suite

### Fixed

- END TEST and ABORT TEST operate on the active test and preserve auditable closeout records.
- Original evidence binaries are immutable.
- Evidence lineage cycles are rejected.
- False metadata-history entries are no longer created for unchanged saves.
- Mobile evidence-workspace containment and modal stacking were corrected.

## Version 0.6.5 — Cross-Batch Hardening

- Reconciled project persistence, recovery, Project Library, and Save As Copy behavior.
- Strengthened evidence binary immutability, lineage, integrity states, and metadata history.
- Strengthened authorization readiness and engagement-status history.
- Restored interactions, field notes, global search, command palette, Project Health, and report-readiness controls.
- Strengthened mapping relationships, coverage, traceability, findings revalidation, and standalone report output.
- Added migration support through Schema 7.

## Version 0.6.0 — Findings and Severity Engine

- Added six-dimension severity analysis, analyst override rationale, confidence, reproducibility, detection likelihood, remediation accountability, controlled finding lifecycle, and positive observations.

## Version 0.5.0 — Field Operations

- Added persistent active-test context, timers, rapid event capture, timeline filters, Daily Field Log, Close Out Day, and outstanding questions.

## Version 0.4.0 — Mapping Workspace

- Added multiple plans, markers, filters, pan and zoom, scale calibration, measurement, zones, paths, and coverage overlays.

## Version 0.3.0 — Site Hierarchy

- Added the canonical Organization → Site → Building → Floor → Zone → Asset model and record-to-location relationships.

## Version 0.2.0 — Persistence Foundation

- Added Indexed Database storage, evidence hashing, project packages, schema migration, and recovery checkpoints.

## Version 0.1.0 — Initial Foundation

- Introduced the local-first project, authorization, tests, timeline, observations, evidence metadata, findings, reporting, and autosave foundations.
