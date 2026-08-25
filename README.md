# SENTINEL — Physical Security Red Team Workbench

**Release:** Version 0.15.0 Release Candidate 2  
**Project schema:** 14  
**Release date:** August 25, 2026  
**Architecture:** Local-first, no-compile browser application

SENTINEL is a field instrument for planning, conducting, documenting, analyzing, and reporting **authorized physical security red team assessments**. It combines a field notebook, test director, evidence workstation, findings register, remediation and retest system, baseline comparator, traceability environment, and governed professional report builder.

The assessment lifecycle is:

**SCOPE → PLAN → RECON → TEST → OBSERVE → EVIDENCE → FINDINGS → REPORT → RETEST**

SENTINEL is designed to document authorized assessment work. It does not provide instructions for bypassing real-world security safeguards.

## Start SENTINEL

1. Extract the release archive.
2. From the extracted directory, start a local static server:

   ```bash
   python -m http.server 8080
   ```

3. Open `http://127.0.0.1:8080/index.html` in a current browser.
4. Create a new project or import a SENTINEL project package.
5. Complete the Authorization and Rules of Engagement Register before operational testing.

Opening `index.html` directly through a `file://` address is suitable only for basic review. A local Hypertext Transfer Protocol (HTTP) origin or static Hypertext Transfer Protocol Secure (HTTPS) host is strongly recommended for dependable Indexed Database (IndexedDB), encryption, media capture, package, recovery, and storage behavior.

## Release-candidate status

Version 0.15.0 Release Candidate 2 is the operational hardening successor to Release Candidate 1. It retains the complete Professional Report Builder 2.0 and corrects issues found during final acceptance work:

- Letter-size report pagination no longer produces a blank second page.
- Printed reports use paged-media headers and reliable **Page X of Y** numbering instead of the former fixed-footer `Page 0` result.
- Report revision creation regenerates nested custom-section and evidence-selection identifiers, eliminating duplicate Universally Unique Identifier (UUID) collisions while preserving visible report content and revision provenance.
- Search and modal dialogs now contain keyboard focus and restore focus to the initiating control.
- Form filters and generated select fields have programmatic labels.
- Mobile checkbox and radio targets meet a 44-pixel interaction target, and reduced-motion preferences are honored.
- Large interactive registers render the first 500 matching rows with a clear disclosure while preserving the complete underlying records for exports and reports.
- Projects above 5,000 material records display a large-project warning instead of silently presenting a potentially unresponsive all-at-once workspace.

This build is suitable for **controlled operational acceptance**. It is not yet Version 1.0 because unrestricted secure-origin, cross-browser, physical-device, fault-injection, assistive-technology, and independent security acceptance remain open.

The earlier package labeled `SENTINEL_v0.14.0.zip` is superseded and should not be treated as the canonical Schema 14 release. Release Candidate 1 is also superseded by this hardening build.

## Professional Report Builder 2.0

Reports are persistent, governed project artifacts rather than temporary summaries regenerated from the current project state.

### Composition

Each report revision preserves:

- Report identity, revision, title, subtitle, client, assessed site, and assessment dates
- Sensitivity marking and handling instructions
- Client branding, logo, header, and footer controls
- Prepared-by, reviewer, approval, and issuing-authority records
- Ordered built-in sections and analyst-created custom sections
- Selected evidence, placement, captions, and display order
- Selected full appendices
- Review, approval, Final Issue, revision, and lifecycle histories
- Material project fingerprint and Final Issue Secure Hash Algorithm 256-bit (SHA-256) fingerprint

Built-in sections cover the Executive Summary, Scope and Authorization, Methodology, Site Overview, Security Architecture, Assessment Coverage, Findings, Positive Observations, Defense in Depth, Remediation Priorities, Formal Retesting, Baseline Comparison, Limitations, Conclusion, Approvals, and Appendices.

### Evidence boundary

Evidence is deliberately selected for report distribution. A report revision can include report-safe derived evidence with a report-specific caption and placement. Original evidence remains immutable in the project.

A controlled report package contains only the evidence explicitly selected for that report. It does **not** silently include the complete Evidence Vault, floor plans, recordings, checkpoints, or project database.

### Governance lifecycle

The report lifecycle is:

**DRAFT → IN REVIEW → APPROVED → FINAL ISSUE**

Final Issue is atomic. SENTINEL applies issue metadata, captures the issued snapshot, calculates the SHA-256 seal, and locks the revision only after all issue gates succeed. A failed transaction leaves the approved revision unchanged rather than partially issued.

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

Chromium-based printing now uses paged-media margin boxes for running markings and `Page X of Y` numbering. Browser implementations differ, so every final PDF still requires a visual issue review.

See `REPORT_BUILDER_GUIDE.md` for the full reporting workflow.

## Major retained capabilities

### Authorization and field operations

- Rules of Engagement Register and visible engagement state
- Authorization-readiness gates and one active test at a time
- Mobile Field Mode, timers, rapid event markers, observations, notes, interactions, and Daily Field Logs
- Safe test completion and abort records
- Direct photograph, video, and audio capture where browser policy permits
- Recoverable pending-capture queue

### Site model and mapping

- Organization → Site → Building → Floor → Zone → Asset hierarchy
- Stable UUIDs and human-readable record identifiers
- Multiple site and floor plans
- Markers, zones, paths, layers, filters, scale calibration, measurements, and coverage overlays
- Relationships from map objects to controls, tests, observations, findings, and Control Chains

### Evidence Workstation

- Binary storage separated from structured metadata
- SHA-256 verification
- Immutable originals and non-destructive derived evidence
- Image annotations, labels, measurements, crop, rotation, blur, and redaction
- Image, text, audio, video, and PDF previews
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
- Sequence-aware comparison and eight security layers
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
- Optional workspace lock and encrypted local project storage
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

## Large-project behavior

SENTINEL retains all project records, but interactive registers intentionally render no more than the first **500 matching rows** at once. Refine filters or use an export for the complete register. The cap currently applies to the generic registers, Evidence Vault, Timeline, Coverage Matrix, and Relationship Gap Queue.

A project-scale profile warns when the project contains more than **5,000 material records**. The warning does not delete, truncate, or alter project data. It identifies when filtering, staged analysis, or a smaller project partition may be necessary for responsive browser use.

Reports and exports are generated from the complete project model and are not limited to the first 500 interactive rows.

## Project schema and compatibility

The current project schema is **14**.

Migration is implemented from every previously published schema:

**1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14**

The release includes historical fixtures derived from Versions 0.1.0 through 0.13.5. All 13 fixtures migrated to Schema 14 and passed the post-migration audit in the final focused matrix.

Projects created by a newer unsupported schema are rejected rather than guessed at or silently downgraded.

## Validation summary

The exact canonical source passed **288 executed assertions across nine focused suites**:

- 31 full-application static assertions
- 50 migration and export assertions
- 29 Report Builder static implementation assertions
- 43 report-governance semantic assertions
- 59 Professional Report Builder browser assertions
- 23 broad release-candidate browser smoke assertions
- 8 controlled report-package inspection assertions
- 24 Release Candidate 2 static hardening assertions
- 21 Release Candidate 2 accessibility, scale, and PDF assertions

The final acceptance matrix covers syntax, duplicate functions and element identifiers, schema migration, report composition, custom-section preservation, nested revision identifiers, selected-evidence boundaries, review and approval, atomic Final Issue, immutable issue snapshots, divergence, new revisions, HTML, Markdown, JSON, report packages, Letter pagination, paged-media numbering, keyboard focus behavior, accessible form names, large-register disclosure, desktop and mobile layout, and material browser errors.

A representative Letter-size report rendered as 14 pages. Page 2 began with the Executive Summary, every page contained report content, and all pages displayed correct `Page X of 14` numbering. The rendered contact sheet and PDF are included in `test-results/`.

The complete inherited secure-origin test suite also ships in the release. The current managed Chromium environment blocks all ordinary browser origins and disables IndexedDB, camera, microphone, video, and printing through enterprise policy. The inherited suite therefore could not be rerun against this exact build here. That boundary is documented in `VALIDATION.md` and is **not** represented as a pass.

## Remaining acceptance before Version 1.0

- Run the complete inherited matrix on an unrestricted local secure origin.
- Complete Firefox, Safari, and WebKit acceptance.
- Test intended phones, tablets, laptops, cameras, microphones, codecs, and permission flows.
- Exercise browser quota, storage exhaustion, interrupted save/import, and corrupt-package/checkpoint recovery.
- Complete keyboard-only and screen-reader acceptance with representative users and assistive technology.
- Test large evidence binaries and representative high-record projects on target hardware.
- Conduct an independent cryptographic, privacy, and application-security review.
- Perform a visual issue review for every representative client report template and final issued PDF.

Use `FINAL_ACCEPTANCE_CHECKLIST.md` to record these gates.

Passphrases are unrecoverable. SENTINEL has no password reset, escrow service, hidden master key, or cloud recovery service.

Browser encryption protects local records and packages at rest, but it cannot protect data from a compromised operating system, malicious browser extension, unlocked session, device administrator, screen capture, memory inspection, or other endpoint compromise.

## Release contents

- `index.html` — complete no-compile application
- `README.md` — application overview and release status
- `REPORT_BUILDER_GUIDE.md` — governed reporting workflow
- `FINAL_ACCEPTANCE_CHECKLIST.md` — remaining Version 1.0 acceptance gates
- `VALIDATION.md` — exact validation record and boundaries
- `REPORT_BUILDER_IMPLEMENTATION_AUDIT.md` — implementation and hardening audit
- `CHANGELOG.md` — release history
- `RELEASE_STATUS.txt` — release-candidate decision
- `RELEASE_VALIDATION_SUMMARY.json` — machine-readable validation summary
- `MANIFEST.json` — file sizes and SHA-256 hashes
- `tests/` — repeatable static, migration, browser, security, persistence, evidence, analysis, remediation, baseline, report, accessibility, PDF, and scale tests
- `test-results/` — focused results, screenshots, representative report outputs, the Letter-size PDF, and its contact sheet
