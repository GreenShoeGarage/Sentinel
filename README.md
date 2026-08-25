# SENTINEL — Physical Security Red Team Workbench

**Release:** Version 0.15.0 Release Candidate 1  
**Project schema:** 14  
**Release date:** August 24, 2026  
**Architecture:** Local-first, no-compile browser application

SENTINEL is a field instrument for planning, conducting, documenting, analyzing, and reporting **authorized physical security red team assessments**. It combines a field notebook, test director, evidence workstation, findings register, remediation and retest system, baseline comparator, traceability environment, and governed professional report builder.

The assessment lifecycle is:

**SCOPE → PLAN → RECON → TEST → OBSERVE → EVIDENCE → FINDINGS → REPORT → RETEST**

SENTINEL is designed to document authorized assessment work. It does not provide instructions for bypassing real-world security safeguards.

## Start SENTINEL

1. Extract the release archive.
2. Open `index.html` in a current browser.
3. For dependable Indexed Database (IndexedDB), encryption, camera, microphone, video, and package behavior, serve the release from `localhost` or a static Hypertext Transfer Protocol Secure (HTTPS) host rather than relying on a `file://` address.
4. Create a new project or import a SENTINEL project package.
5. Complete the Authorization and Rules of Engagement Register before beginning operational testing.

A simple local server can be started from the release directory with:

```bash
python -m http.server 8080
```

Then open `http://127.0.0.1:8080/index.html` in the browser.

## Release-candidate status

Version 0.15.0 Release Candidate 1 is the first package in this development line that contains the **actual Project Schema 14 Professional Report Builder 2.0 implementation**.

The previously distributed file labeled `SENTINEL_v0.14.0.zip` is superseded. During the final review, its application source was found to still identify itself as Version 0.13.5 / Project Schema 13, and its validation record showed that most Report Builder 2.0 gates had not passed. Do not use that package as the canonical reporting release.

This release candidate corrects that mismatch and provides reconciled source, documentation, tests, validation records, version labels, schema labels, and manifest hashes.

## Professional Report Builder 2.0

Reports are persistent, governed project artifacts rather than temporary summaries regenerated from the current project state.

### Composition

Each report revision preserves:

- Report identity, revision, title, subtitle, client, assessed site, and assessment dates
- Sensitivity marking and handling instructions
- Client branding, logo, header, and footer controls
- Prepared-by, reviewer, approval, and issuing-authority records
- Ordered built-in sections
- Analyst-created custom sections
- Selected evidence, placement, captions, and display order
- Selected full appendices
- Review, approval, Final Issue, revision, and lifecycle histories
- Material project fingerprint and Final Issue Secure Hash Algorithm 256-bit (SHA-256) fingerprint

Built-in sections cover the executive summary, scope and authorization, methodology, site overview, security architecture, assessment coverage, findings, positive observations, defense in depth, remediation priorities, formal retesting, baseline comparison, limitations, conclusion, approvals, and appendices.

### Evidence boundary

Evidence is deliberately selected for report distribution. A report revision can include report-safe derived evidence with a report-specific caption and placement. Original evidence remains immutable in the project.

A controlled report package contains only the evidence explicitly selected for that report. It does **not** silently include the complete Evidence Vault, floor plans, recordings, checkpoints, or project database.

### Governance lifecycle

The report lifecycle is:

**DRAFT → IN REVIEW → APPROVED → FINAL ISSUE**

Final Issue is an atomic transaction. SENTINEL applies issue metadata, captures the issued snapshot, calculates the SHA-256 seal, and locks the revision only after all issue gates succeed. A failed issue transaction leaves the approved revision unchanged rather than partially issued.

After Final Issue:

- The issued revision is read-only.
- The exact issued snapshot and issue fingerprint remain preserved.
- Material changes to the live project produce a visible divergence warning.
- Live-project divergence does not rewrite or invalidate the sealed issue record.
- Further changes begin in a new Draft revision linked to the prior issue.

The SHA-256 seal provides project-model tamper evidence. It is not a legally qualified digital signature.

### Output formats

The governed report artifact drives:

- Interactive report preview
- Standalone Hypertext Markup Language (HTML)
- Markdown
- Structured JavaScript Object Notation (JSON)
- Browser print-to-Portable Document Format (PDF)
- Controlled report-package ZIP export

Every final PDF should receive a visual issue review because pagination can vary by browser, operating system, paper size, scaling, fonts, and print driver.

See `REPORT_BUILDER_GUIDE.md` for the complete reporting workflow.

## Major retained capabilities

### Authorization and field operations

- Rules of Engagement Register and visible engagement state
- Authorization-readiness gates
- One active test at a time
- Mobile Field Mode, timers, rapid event markers, observations, notes, interactions, and Daily Field Logs
- Safe test completion and abort records
- Direct photograph, video, and audio capture where browser policy permits
- Recoverable pending-capture queue

### Site model and mapping

- Organization → Site → Building → Floor → Zone → Asset hierarchy
- Stable Universally Unique Identifiers (UUIDs) and human-readable record identifiers
- Multiple site and floor plans
- Markers, zones, paths, layers, filters, scale calibration, measurements, and coverage overlays
- Relationships from map objects to controls, tests, observations, findings, and Control Chains

### Evidence Workstation

- Binary storage separated from structured metadata
- Secure Hash Algorithm 256-bit verification
- Immutable originals and non-destructive derived evidence
- Image annotations, labels, measurements, crop, rotation, blur, and redaction
- Image, text, audio, video, and Portable Document Format previews
- Provenance, verification history, custody history, metadata history, transformation history, and lineage
- Evidence Vault and Photo Log

### Findings and assurance

- Multidimensional severity model with analyst override rationale
- Confidence, reproducibility, detection, consequence, remediation, and lifecycle controls
- Positive Observations Register
- Coverage Matrix, evidence-sufficiency states, relationship-gap queue, completeness review, and analyst sign-off
- Visual Traceability Graph and bidirectional Traceability Inspector

### Control Chains and defense in depth

- Expected-versus-observed protection paths
- Sequence-aware comparison
- Eight security layers
- Separate control degradation and evidence limitation analysis
- Report-ready path and layer diagrams

### Remediation, retesting, and baselines

- Immutable remediation submissions
- Governed formal retest authorization, execution, completion, and independent review
- Multiple corrective or follow-up retests
- Finding closure and reopening history
- Complete immutable assessment baselines
- Field-level semantic comparison, regression and improvement prompts, deletion versus unexplained absence, review dispositions, and comparison seals

### Local-first security and recovery

- IndexedDB project and binary storage
- Project Library, autosave, checkpoints, recovery, Save As Copy, and complete project packages
- Optional workspace lock
- Optional encrypted local project storage
- Optional encrypted `.sentinel.enc` project packages
- Advanced Encryption Standard in Galois/Counter Mode (AES-GCM)
- Password-Based Key Derivation Function 2 (PBKDF2) with a user-provided passphrase
- Storage quota monitoring and Emergency Export
- No telemetry, analytics, account, or mandatory cloud service

## Project packages and report packages

These exports serve different purposes:

- A **project package** is a complete backup and working record. It can contain structured project data, evidence, maps, checkpoints, baselines, and operational history.
- A **report package** is a controlled distribution artifact. It contains governed report outputs, issue metadata, a manifest, and only explicitly selected report evidence.

Do not treat a report package as a project backup. Do not distribute a complete project package merely because a client needs a report.

## Project schema and compatibility

The current project schema is **14**.

Migration is implemented from every previously published schema:

**1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14**

The release includes historical fixtures derived from Versions 0.1.0 through 0.13.5. All 13 fixtures migrated to Schema 14 and passed the post-migration audit in the final release-candidate matrix.

Projects created by a newer, unsupported schema are rejected rather than guessed at or silently downgraded.

## Validation summary

The exact release tree passed **243 executed assertions across seven suites**:

- 31 full-application static assertions
- 50 migration and export assertions
- 29 report static assertions
- 43 report-governance semantic assertions
- 59 Professional Report Builder browser assertions
- 23 broad release-candidate browser smoke assertions
- 8 controlled report-package inspection assertions

These checks cover source syntax, duplicate functions and element identifiers, migration, report composition, custom-section preservation, selected-evidence boundaries, review and approval, atomic Final Issue, immutable issue snapshots, divergence, new revisions, HTML, Markdown, JSON, print styling, report-package contents and hashes, workflow navigation, desktop and mobile layout, and material browser errors.

The release also contains the inherited secure-origin test suite. The current managed validation environment blocks all ordinary browser origins and denies IndexedDB, camera, microphone, printing, and video through enterprise Chromium policy. Therefore the complete inherited secure-origin browser matrix could not be rerun against this exact release in this environment. That boundary is documented in `VALIDATION.md`; it is not represented as a pass.

## Operational limitations before Version 1.0

Version 0.15.0 Release Candidate 1 is not yet the final controlled operational release. Remaining acceptance work includes:

- Full inherited suite on an unrestricted secure local origin
- Firefox, Safari, and WebKit acceptance
- Physical phone, tablet, laptop, camera, microphone, and codec testing
- Browser quota, storage exhaustion, interrupted save/import, and corrupt-package recovery drills
- Keyboard-only and screen-reader review
- Large-project and large-evidence performance profiling
- Independent cryptographic and security review
- Visual issue review of representative final PDFs

Passphrases are unrecoverable. SENTINEL has no password reset, escrow service, hidden master key, or cloud recovery service.

Browser encryption protects local records and packages at rest, but it cannot protect data from a compromised operating system, malicious browser extension, unlocked session, device administrator, screen capture, memory inspection, or other endpoint compromise.

## Release contents

- `index.html` — complete no-compile application
- `README.md` — application overview and release status
- `REPORT_BUILDER_GUIDE.md` — governed reporting workflow
- `VALIDATION.md` — exact validation record and boundaries
- `REPORT_BUILDER_IMPLEMENTATION_AUDIT.md` — implementation gate audit
- `CHANGELOG.md` — release history
- `RELEASE_STATUS.txt` — release-candidate decision
- `RELEASE_VALIDATION_SUMMARY.json` — machine-readable validation summary
- `MANIFEST.json` — file sizes and SHA-256 hashes
- `tests/` — repeatable static, migration, browser, security, persistence, evidence, analysis, remediation, baseline, and report tests
- `test-results/` — final focused results, screenshots, and sample governed report outputs
