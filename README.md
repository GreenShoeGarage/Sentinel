# SENTINEL — Physical Security Red Team Workbench

**Application version:** 0.13.5
**Project schema:** 13
**Release:** Interface Consolidation and Workflow Cleanup
**Architecture:** local-first, no compile step, no account, no telemetry

SENTINEL is a browser-based Field Instrument for planning, conducting, documenting, analyzing, and reporting **authorized physical security red team assessments**. It combines an Authorization and Rules of Engagement Register, hierarchical site model, floor-plan workspace, test director, field recorder, Evidence Workstation, findings and severity engine, Assessment Assurance workbench, traceability graph, defense-in-depth analysis, remediation and formal retesting, immutable baseline comparison, secure local storage, and professional report exports.

SENTINEL is designed to document authorized professional activity. It does not provide instructions for bypassing locks, alarms, access-control systems, surveillance, or other physical safeguards. Control Chains describe defensive relationships, expected behavior, observed assessment results, and evidence limitations—not operational bypass sequences.

Version 0.13.5 is a cross-module interface consolidation and usability release. It preserves Project Schema 13 and every Version 0.13.0 capability while reorganizing the application around the assessment lifecycle, consolidating project-file operations, making navigation and traceability panels adjustable, correcting desktop and mobile shell defects, adding dashboard guidance, and expanding repeatable user-interface regression coverage.

## Run SENTINEL

No build process is required. Serve the release folder as a normal static site so the browser has a dependable origin for the Indexed Database application programming interface (IndexedDB), Web Cryptography application programming interface, camera, and microphone permissions.

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080/index.html`.

The folder may also be deployed to any conventional static host. No server-side application, remote database, cloud service, or account system is required.

Opening `index.html` directly through a `file:` address may work in some browsers, but protected storage and media behavior vary. A local or hosted Hypertext Transfer Protocol Secure (HTTPS) origin is preferred. Browsers generally treat `http://localhost` and `http://127.0.0.1` as secure development contexts.

## Recommended first-use sequence

1. Create or import a project.
2. Complete Project Details, the Authorization and Rules of Engagement Register, and the current operator.
3. Configure the **Organization → Site → Building → Floor → Zone → Asset** hierarchy.
4. Add security controls and planned tests.
5. Configure **Security & Storage** in Advanced Mode, create an encrypted backup, and test lock and restore behavior on the intended field device.
6. Conduct authorized tests, capture events and evidence, and document observations and findings.
7. Review **Assessment Assurance** for coverage gaps, evidence sufficiency, limitations, and analyst sign-off.
8. Model relevant **Control Chains** and defense layers where combined control behavior matters.
9. Freeze a clearly named baseline at each important assessment or remediation milestone.
10. Record remediation submissions without changing the original finding.
11. Plan, authorize, execute, complete, and independently review formal retests.
12. Compare the appropriate baselines, disposition every regression and review item, and sign the comparison conclusion.
13. Generate final reports only after report-readiness, assurance, retest-review, and baseline-comparison checks pass.

## Authorization and safety model

Every project contains an Authorization and Rules of Engagement Register covering the client, sponsor, authorization authority, assessment team, facilities, areas, techniques, times, interactions, photography, recording, social engineering, tailgating, hardware testing, vehicle testing, alarm testing, radio-frequency testing, safety restrictions, stop-work conditions, escalation, law-enforcement coordination, and evidence handling.

Engagement states are visible throughout the interface:

- `PLANNING`
- `AUTHORIZED`
- `ACTIVE`
- `PAUSED`
- `STOPPED`
- `COMPLETE`

Operational tests require current authorization readiness and operator acknowledgement. Direct camera, video, and audio capture additionally requires acknowledgement of the project’s photography or recording restrictions. Pausing an engagement prevents new operational activity while still allowing an active test to be safely ended or aborted.

Formal retests have their own authorization reference, authority, restrictions, safety and stop-work conditions, planned method, and authorized period. Starting a formal retest requires the engagement to be `AUTHORIZED` or `ACTIVE`, and only one formal retest may be `IN PROGRESS` at a time.

## What Version 0.13.5 changes

### Workflow-centered navigation

Advanced Mode is no longer presented as one flat list of equally weighted tools. Navigation is organized into five operational groups:

- **Workspace** — Dashboard, Project, Map, Controls, and Tests
- **Fieldwork** — Field Mode, Observations, Evidence, Field Log, Timeline, Interactions, and Field Notes
- **Analysis** — Findings, Assessment Assurance, Traceability, and Control Chains
- **Closeout** — Remediation and Retest, Baselines, and Report
- **Administration** — Registers and Security & Storage

Easy Mode keeps the smaller essential workflow without removing project data. Record-count and attention badges expose work that requires review without turning the sidebar into a dashboard.

### Consolidated project operations

New Project, Open Project, Save Now, Save As Copy, plain and encrypted package export, Emergency Export, Import, checkpoints, and recovery are consolidated into one **Project** menu. The sidebar retains one clear **Project files & backups** entry instead of ten competing file-operation buttons. Existing action identifiers and package behavior remain compatible with the regression suite.

### Adjustable workspace shell

- The desktop navigation and Traceability Inspector can be collapsed independently.
- Both desktop panels can be resized; widths persist as device-local interface preferences.
- The Traceability Inspector stays closed until it is useful, opens automatically for selected records on wide screens, and behaves as an explicit drawer on smaller screens.
- Selecting a new destination resets the workspace scroll position instead of inheriting stale scroll from the previous screen.
- Sticky contextual headers keep the current module, purpose, and primary actions visible.

Interface preferences are not assessment records and are intentionally excluded from project packages and schema migration.

### Dashboard guidance

The Dashboard now presents the full lifecycle:

**SCOPE → PLAN → RECON → TEST → OBSERVE → EVIDENCE → FINDINGS → REPORT → RETEST**

It identifies the next useful action from the current project state, keeps high-frequency record creation close at hand, and leaves report-readiness, remediation, coverage, and project-health information visible without forcing the analyst to infer the intended sequence.

### Mobile and accessibility cleanup

Version 0.13.5 corrects the mobile application grid so the classification banner, workspace, and footer no longer overlap. It adds a dedicated drawer header and close control, a compact footer, mobile-safe action bars and modals, stronger focus indicators, current-page semantics, a skip link, expanded-state reporting, and overflow protections. Empty inspector drawers close automatically on small screens rather than blocking the workspace.

### Corrected regressions found during cleanup

The new cleanup suite caught and corrected several defects before release:

- Collapsing the desktop navigation could reflow the main workspace into a zero-width grid column.
- Clicking text inside the new Search button could immediately close the command palette.
- A selected record could leave an empty inspector backdrop blocking mobile navigation.
- The previous mobile grid definition allowed the classification banner and footer to collide with content.
- Direct test automation for Save As Copy and package export needed to use the consolidated Project menu.

## Inherited Batch 11 capability: Baseline Comparison and Regression Analysis

### Immutable assessment baselines

A baseline is now a complete frozen assessment snapshot rather than a collection of record counts. It preserves:

- Project and scope
- Authorization and Rules of Engagement
- Assessment Assurance records and sign-off
- Site hierarchy
- Security controls
- Tests and timeline events
- Observations and evidence metadata
- Findings and positive observations
- Interactions, assumptions, issues, field notes, questions, and Daily Field Logs
- Remediation submissions and formal retests
- Control Chains and defense-layer assessments
- Map plans, markers, zones, paths, and relationships
- Record tombstones used to explain deliberate removal

Each baseline receives:

- Persistent Universally Unique Identifier (UUID) and human-readable baseline code
- Creator, timestamp, name, and note
- Source application and schema version
- Source project update timestamp
- SHA-256 snapshot hash
- Sealing and verification history
- Active or Retired status

The baseline snapshot is immutable. Retirement preserves the snapshot and hash while removing it from normal selection emphasis. Restoring a retired baseline does not rewrite its contents.

### Baseline integrity verification

SENTINEL serializes material snapshot content deterministically and seals it with SHA-256. Integrity checks distinguish:

- `VERIFIED`
- `MISMATCH`
- `UNSEALED`
- `RETIRED`

A comparison cannot be signed until both source baselines pass integrity verification. Imported and recovered projects normalize and seal legacy baseline records before they can participate in the Schema 13 comparison workflow.

The hashes provide project-model tamper evidence. They are not legally qualified digital signatures and do not independently prove that an analyst’s conclusion is correct.

### Semantic comparison, not count-only comparison

The **Baselines & Regression Analysis** workspace compares:

- One immutable baseline against another immutable baseline
- An immutable baseline against the current live project

Comparison is performed at the record and material-field level. SENTINEL first uses stable UUID relationships and then uses persistent human-readable identifiers where appropriate to help match records across historical project copies.

Comparison categories include:

- Project and scope
- Authorization and Rules of Engagement
- Assessment Assurance
- Coverage metrics
- Site hierarchy
- Security controls
- Test cases
- Timeline events
- Observations
- Evidence
- Findings
- Positive observations
- Interactions
- Assumptions
- Issues
- Daily Field Logs
- Field notes
- Remediation submissions
- Formal retests
- Control Chains
- Map plans, markers, zones, and paths

Material differences expose the field, prior value, later value, automatic impact suggestion, analyst disposition, rationale, owner, and review state.

### Regression, improvement, review, and neutral impact

SENTINEL suggests one of four analytical impacts for every material change:

- `REGRESSION`
- `IMPROVEMENT`
- `REVIEW`
- `NEUTRAL`

Examples include:

- A passing test becoming failed or inconclusive
- A finding increasing in severity
- Evidence losing availability or changing its recorded hash
- A remediation state moving toward verified closure
- Coverage percentages increasing or decreasing
- Authorization, scope, map, or sampling changes requiring human review

Automatic classifications are analytical prompts. They do not replace professional judgment. The analyst may change the classification, but every regression or review item must have a disposition, rationale, and accountable owner before the comparison can be signed.

### Deliberate deletion versus unexplained absence

Schema 13 adds first-class record tombstones. Where a supported deletion workflow records a tombstone, comparison reports the record as:

- `DELETED` — the project records who removed the record, when it was removed, and why

When a record disappears without a corresponding tombstone, comparison reports:

- `ABSENT_LATER` — the later snapshot does not contain the record and the reason is not established

This prevents SENTINEL from silently treating every missing record as an intentional deletion. Absence remains a review condition until the analyst establishes what happened.

### Coverage regression analysis

Each endpoint receives a comparable Assessment Assurance coverage summary, including:

- Planned tests
- Attempted tests
- Completed tests
- Attempted tests with evidence
- Test evidence percentage
- Total and covered controls
- Control coverage percentage
- Total and assessed locations
- Location coverage percentage
- Open blocking gaps
- Accepted limitations

The comparison workspace shows the before value, after value, numeric delta, and the direction of material change. Lower values are treated as favorable only for metrics where lower is genuinely better, such as open blocking gaps.

### Comparison review workflow

A saved comparison is a first-class project record with:

- UUID and comparison code
- Named source and destination baselines
- Purpose
- Per-change classification, disposition, rationale, owner, reviewer, and timestamp
- Overall analyst conclusion
- Review history
- Source baseline hashes
- SHA-256 review value
- Fast in-session staleness fingerprint

The workflow is:

**DRAFT → REVIEWED**

A comparison remains Draft while material regressions or review items are unresolved. Signing requires:

- Both endpoint baselines to verify successfully
- A disposition, rationale, and owner for every `REGRESSION` and `REVIEW` item
- An overall comparison conclusion
- Current analyst attribution

A material change to the comparison record, its dispositions, or either endpoint invalidates the current review state. SENTINEL then labels the comparison stale and requires a new review.

### Review log, filtering, and exports

The workspace includes:

- **Compare** — endpoint selection, summary cards, coverage deltas, category overview, filters, and the change register
- **Snapshots** — immutable snapshot register, integrity state, verification, export, retirement, and comparison actions
- **Review Log** — saved Draft, Reviewed, and stale comparison records

Filters include category, impact, change type, and free-text search.

Exports include:

- Structured JSON comparison package
- CSV change register
- Standalone HTML comparison report
- Individual baseline JSON snapshot

### Report and readiness integration

Reviewed, current baseline comparisons can appear in:

- Interactive report preview
- Standalone HTML assessment report
- Markdown assessment report
- Browser print-to-PDF output

The report section includes endpoint identities, comparison conclusion, regression and improvement counts, material-change register, reviewer attribution, timestamp, and review SHA-256 value.

Final report readiness identifies Draft or stale baseline comparisons when they are intended to support the current assessment conclusion. Preview output may include incomplete records only when the project’s explicit Draft-inclusion option is enabled.

## Other major capabilities retained

### Local-first persistence and recovery

- IndexedDB project and binary storage
- Visible autosave states
- Project Library and Save As Copy
- Recovery checkpoints
- Project Health audits
- Plain `.sentinel` and encrypted `.sentinel.enc` project packages
- Schema detection, validation, migration, and recovery safeguards

### Secure workspace and field capture

- Optional Advanced Encryption Standard in Galois/Counter Mode (AES-GCM) encrypted local storage
- Password-Based Key Derivation Function 2 with Secure Hash Algorithm 256-bit (PBKDF2-SHA-256) passphrase derivation
- Workspace lock, inactivity lock, and hidden-tab lock
- Encrypted pending-capture queue
- Direct photograph, video, and audio capture where supported
- Storage quota monitoring and emergency export
- Classification and handling banners

### Site model and mapping

- Organization, Site, Building, Floor, Zone, and Asset hierarchy
- Multiple floor or site plans
- Portable Network Graphics, Joint Photographic Experts Group, Scalable Vector Graphics (SVG), and browser-rendered Portable Document Format plans
- Markers, zones, paths, scale calibration, measurements, pan, zoom, and coverage overlays
- Direct relationships to controls, tests, observations, evidence, findings, and Control Chains

### Field operations

- Test Case Manager
- Authorization-aware Field Mode
- Live timer and rapid event markers
- Safe completion and abort
- Unified timeline
- Observations, interactions, field notes, issues, assumptions, questions, and Daily Field Logs

### Evidence Workstation

- Immutable original evidence
- SHA-256 hashing and verification history
- Chain of custody and acquisition provenance
- Image, audio, video, text, and Portable Document Format preview
- Non-destructive annotation, measurement, redaction, blur, crop, rotation, and undo
- Original-to-derived lineage and comparison
- Bulk organization and relationship assignment
- Photo Log and embedded report images

### Findings, severity, and positive observations

- Six-dimension suggested severity model
- Analyst overrides with rationale
- Confidence and reproducibility
- Controlled finding lifecycle
- Material-change revalidation
- Remediation ownership and target dates
- Positive Observations Register

### Assessment Assurance and traceability

- Multidimensional Coverage Matrix
- Relationship Gap Queue
- Evidence-sufficiency states
- Accepted limitations with owner and rationale
- Completeness checklist
- Analyst sign-off and staleness detection
- Visual upstream and downstream Traceability Graph
- JSON, CSV, and SVG exports

### Control Chains and defense in depth

- Ordered expected and observed protection paths
- Eight canonical defense layers
- Worked, Partially Worked, Failed, Not Tested, and Insufficient Evidence states
- Sequence-aware comparison
- Separate control-interaction and evidence-limitation candidates
- Review lifecycle, report diagrams, map links, traceability, and baseline preservation

### Remediation and formal retesting

- Immutable remediation submissions and recommendation snapshots
- Governed retest planning and authorization
- Immutable completion records and SHA-256 fingerprints
- Independent reviewer separation and sign-off
- Multiple corrective or follow-up retests
- Finding closure and reopening history
- Recommendation-to-retest traceability

### Reporting

- Interactive report preview
- Standalone HTML report
- Markdown report
- Browser printing to Portable Document Format (PDF)
- Executive summary, scope, authorization, findings, positive observations, assurance disclosures, Control Chains, remediation, formal retesting, baseline comparison, Photo Log, and appendices

## Project schema and compatibility

Version 0.13.5 uses **Project Schema 13**.

Migration is supported from every previously published SENTINEL schema:

- Schema 1 — Version 0.1.0
- Schema 2 — Version 0.2.0
- Schema 3 — Version 0.3.0
- Schema 4 — Version 0.4.0
- Schema 5 — Version 0.5.0
- Schema 6 — Version 0.6.0
- Schema 7 — Version 0.6.5
- Schema 8 — Version 0.7.0
- Schema 9 — Version 0.9.0
- Schema 10 — Version 0.10.0
- Schema 11 — Version 0.11.0
- Schema 12 — Version 0.12.0

Schema 12 migration creates the baseline-comparison and record-tombstone collections, normalizes historical snapshots into the complete Schema 13 snapshot shape, and seals previously unsealed baselines before they participate in reviewed comparisons.

Projects from a newer unsupported schema are rejected rather than guessed at. Imported projects are migrated, normalized, audited, and validated before replacing the active project, with recovery checkpoints retained where possible.

## Validation

The release contains a repeatable static and browser acceptance suite under `tests/`.

Validated totals:

- **31 static assertions**
- **504 browser assertions**
- **535 total assertions**
- **21 isolated browser suites**

The automated acceptance environment used Chromium 144.0.7559.96 on a normal local Hypertext Transfer Protocol origin. The suite includes historical fixtures for Schemas 1 through 12, real IndexedDB and Web Cryptography operations, deterministic fake camera and microphone devices, and end-to-end baseline comparison, remediation, retesting, evidence, assurance, and secure-storage acceptance.

Run the complete suite from the release root:

```bash
python -m pip install -r tests/requirements.txt
python tests/run_all.py
```

For a conservative single-process run:

```bash
SENTINEL_TEST_JOBS=1 SENTINEL_TEST_TIMEOUT=720 python tests/run_all.py
```

See `VALIDATION.md` and `tests/README.md` for exact suites, fixtures, commands, and limitations.

## Security and operational limitations

- Passphrases are unrecoverable. SENTINEL has no escrow, reset service, or hidden master key.
- Encryption uses browser Web Cryptography primitives but has not undergone an independent cryptographic or penetration-testing review.
- SENTINEL does not use a hardware-backed key store, operating-system biometric unlock, or multi-user identity system.
- A compromised browser, operating system, extension, device, or active unlocked session can expose decrypted project data.
- Screen lock without encrypted local storage is not at-rest protection.
- Logical deletion cannot guarantee secure erasure from flash storage, backups, synchronization, page files, crash dumps, or forensic remnants.
- Cryptographic operations and package creation operate in browser memory. Evidence imports have a 512 mebibyte safety cap and warn above 100 mebibytes; practical limits can be much lower on mobile devices.
- Direct capture requires browser permission and a secure context. Supported codecs and camera-selection behavior vary by browser and device.
- A capture can still be lost before successful IndexedDB staging if the browser closes, power is lost, or storage is exhausted.
- Browser storage quota and persistence decisions remain under browser and operating-system control.
- Automated browser acceptance currently covers Chromium. Firefox, Safari, WebKit, and physical target devices require acceptance before operational reliance.
- Independent review and cryptographic fingerprints improve record integrity but do not constitute a legally qualified digital-signature system.
- Automatic baseline impact classifications are heuristic analytical prompts. The analyst remains responsible for establishing materiality, causation, and significance.
- Matching across historical records depends primarily on stable UUIDs and secondarily on persistent human-readable identifiers. Poorly migrated or manually rewritten identifiers can require analyst reconciliation.
- A tombstone explains only deletions recorded through a supporting deletion workflow. An unexplained absence remains a separate review item.
- Baseline snapshots contain project records and evidence metadata, relationships, and hashes; they do not duplicate every stored evidence binary inside each baseline.
- SENTINEL cannot verify that an assessment, remediation, retest, baseline disposition, or report conclusion is technically correct; professional review remains essential.
- The complete drag-and-drop report composer remains a future roadmap item.
- SENTINEL is not a substitute for legal review, safety planning, client authorization, evidence policy, cybersecurity controls, secure device management, or professional judgment.

## Reassessed development roadmap

The application is now best treated as a **late-beta operational workbench**. The foundational data, authorization, field, evidence, assurance, control-chain, remediation, retest, baseline, encryption, and package models are substantial. The remaining work should focus on acceptance, reporting composition, and release hardening rather than adding another broad analytical subsystem.

### Version 0.13.6 — Operational usability acceptance

- Structured field-device trials on intended phones, tablets, and laptops
- Firefox, Safari, and WebKit acceptance
- Keyboard-only and screen-reader review
- Large-project, large-evidence, and browser-quota performance benchmarks
- Remaining terminology, density, and high-frequency workflow refinements informed by actual users

### Version 0.14.0 — Professional Report Builder 2.0: composition

- Dedicated executive-summary, methodology, limitations, conclusion, and approval records
- Section ordering and inclusion controls
- Selected evidence placement and captions
- Client branding, sensitivity markings, prepared-by, reviewed-by, and approval blocks
- Draft, review, issue, and revision lifecycle

### Version 0.14.5 — Professional Report Builder 2.0: rendering and packages

- Reliable page breaks, headers, footers, numbering, tables, and full appendices
- Report-ready Control Chain, coverage, remediation, retest, and baseline-comparison figures
- Final-issue locking and revision history
- Portable report packages containing only explicitly selected derived evidence

### Version 0.15.0 — Release candidate hardening

- Corrupt-package, interrupted-save, quota-exhaustion, and recovery drills
- Performance and memory profiling
- Complete migration regression from every published schema
- Security and privacy threat-model review
- Guided sample project, Fresh Start, Clear Sample Data, and deployment documentation
- Release candidate acceptance on supported browser and device profiles

### Version 1.0 — Controlled operational release

Version 1.0 should be declared only after the target-browser and target-device matrix passes, the report builder can issue a professional assessment without rebuilding it elsewhere, recovery and migration exercises pass, and no known blocking field workflow remains.

## Release files

- `index.html` — complete no-compile application
- `README.md` — operating, security, and capability guide
- `CHANGELOG.md` — release history
- `VALIDATION.md` — acceptance record
- `MANIFEST.json` — release inventory and SHA-256 values
- `tests/` — reproducible validation suite, historical fixtures, and local media assets
