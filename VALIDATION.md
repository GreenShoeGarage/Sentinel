# SENTINEL Version 0.15.0 Release Candidate 2 Validation Record

**Project schema:** 14  
**Validation date:** August 25, 2026  
**Release decision:** Ready for controlled operational acceptance. Not yet approved as Version 1.0.

## Release purpose

Release Candidate 2 hardens the reconciled Professional Report Builder 2.0 release without changing Project Schema 14. The acceptance work focused on reporting correctness, accessibility, keyboard behavior, large-project responsiveness, report-revision integrity, and release reconciliation.

The earlier `SENTINEL_v0.14.0.zip` package remains superseded because its application source did not contain the claimed Schema 14 implementation. Version 0.15.0 Release Candidate 1 is also superseded by this hardening build.

## Executed focused validation matrix

| Suite | Assertions | Result |
|---|---:|---|
| Full-application static validation | 31 | PASS |
| Schema migration and export validation | 50 | PASS |
| Report Builder static implementation checks | 29 | PASS |
| Report-governance semantic source checks | 43 | PASS |
| Professional Report Builder browser acceptance | 59 | PASS |
| Broad release-candidate browser smoke | 23 | PASS |
| Controlled report-package inspection | 8 | PASS |
| Release Candidate 2 static hardening checks | 24 | PASS |
| Release Candidate 2 accessibility, scale, and PDF acceptance | 21 | PASS |
| **Executed total** | **288** | **PASS** |

These are executed assertions across nine suites. Some suites deliberately examine the same critical surface through different techniques; the total is a count of executed checks, not a claim that every check is unique.

## Defects and weaknesses corrected

### Letter-size report pagination

The prior cover geometry could force a blank second page when a report was printed to United States Letter paper. The cover minimum height was reduced from 245 millimeters to 235 millimeters, with print rules added for heading cohesion, paragraph widows and orphans, repeating table headers, and long-cell wrapping.

The representative report now renders as 14 content-bearing Letter pages. Page 2 begins with **Executive Summary**.

### Reliable page numbering

The former fixed-position footer attempted to use a page counter in normal document content. Chromium rendered that counter as `Page 0` on every page.

Release Candidate 2 uses Cascading Style Sheets (CSS) paged-media margin boxes with `counter(page)` and `counter(pages)`. The representative PDF displays `Page 1 of 14` through `Page 14 of 14`. The false `Page 0` footer is removed.

### Report revision identifier integrity

Creating a new report revision copied nested custom-section and evidence-selection identifiers from the prior revision, which could create duplicate project UUIDs.

New revisions now regenerate nested identifiers, remap custom section ordering and visibility, preserve the visible section and evidence content, and record the normalization in lifecycle history. The full Report Builder browser suite passes without duplicate-identifier audit errors.

### Accessibility and keyboard behavior

The following were corrected or strengthened:

- Generated select fields now associate labels with controls.
- Known filters have accessible names.
- The command palette is an accessible modal dialog with hidden-state semantics.
- Keyboard focus remains contained in the command palette and record modals.
- Closing either surface restores focus to the initiating control.
- Checkbox and radio controls use 18-pixel control geometry.
- Mobile checkbox and radio labels provide a 44-pixel target.
- Reduced-motion preferences suppress nonessential transitions and animations.

Focused browser acceptance visited Project, Evidence, Timeline, Findings, Assessment Assurance, Traceability, Remediation and Retest, and Security workspaces and found no visible unlabeled form controls in the audited surfaces.

### Large-project guardrails

Exploratory synthetic profiling showed increasing cost from all-at-once rendering:

| Records per principal register | Initial data/render | Coverage | Traceability | End-to-end wall time |
|---:|---:|---:|---:|---:|
| 50 | 297 ms | 38 ms | 109 ms | 0.64 s |
| 100 | 501 ms | 105 ms | 162 ms | 1.12 s |
| 250 | 1.39 s | 575 ms | 612 ms | 3.09 s |
| 500 | 3.58 s | 1.33 s | 2.14 s | 7.91 s |

An exploratory 2,000-record-per-register run exceeded the five-minute harness ceiling. Release Candidate 2 therefore does not pretend that unconstrained Document Object Model rendering is acceptable at that scale.

Interactive registers now render the first 500 matching rows and show a visible disclosure. The complete records remain in the project and are used by exports and reports. A project-scale profile activates above 5,000 material records and warns the analyst to filter or partition the work.

The focused scale test confirmed that 600 records were retained while exactly 500 rows rendered, and that a 5,002-record synthetic project activated the large-project state.

## Professional Report Builder acceptance

The reporting matrix verified:

- Persistent Schema 14 report artifact
- Report identity, branding, markings, narratives, ordered built-in sections, and custom sections
- Custom-section preservation through normalization and revision creation
- Unique nested identifiers in new revisions
- Explicit evidence selection, captions, placement, and ordering
- Full appendix controls
- Draft, In Review, Approved, and Final Issue lifecycle
- Review and approval attribution and rationale
- Approval-fingerprint verification
- Transactionally atomic Final Issue behavior
- SHA-256 issue seal
- Read-only issued revision and immutable issued snapshot
- Live-project divergence detection without rewriting the issue
- New Draft revision linked to the prior issue
- Standalone HTML, Markdown, and structured JSON output
- Print-to-PDF styles, Letter pagination, margin-box headers, and Page X of Y numbering
- Controlled report-package ZIP creation
- Package manifest and output-hash verification
- Inclusion of exactly the selected evidence binary
- Exclusion of unrelated evidence and the full project database
- Desktop and mobile Report Builder containment
- Absence of uncaught material browser errors

## Representative PDF acceptance

Artifact: `test-results/rc2_representative_letter_report.pdf`

- Page size: United States Letter
- Pages: 14
- Openable: yes
- Encrypted: no
- Scanned-image-only: no
- Page 2: contains Executive Summary and is not blank
- Accidental blank pages: none
- Numbering: Page 1 of 14 through Page 14 of 14
- Render inspection: completed through the PDF render workflow
- Contact sheet: `test-results/rc2_representative_letter_report_contact_sheet.jpg`

The representative output is a test artifact, not a client-issued report. Every final client PDF must still undergo a visual issue review.

## Migration coverage

Thirteen historical fixtures derived from earlier releases were migrated:

- Schema 1 / Version 0.1.0
- Schema 2 / Version 0.2.0
- Schema 3 / Version 0.3.0
- Schema 4 / Version 0.4.0
- Schema 5 / Version 0.5.0
- Schema 6 / Version 0.6.0
- Schema 7 / Version 0.6.5
- Schema 8 / Version 0.7.0
- Schema 9 / Version 0.9.0
- Schema 10 / Version 0.10.0
- Schema 11 / Version 0.11.0
- Schema 12 / Version 0.12.0
- Schema 13 / Version 0.13.5

Every fixture reached Schema 14 and passed the post-migration project audit. The suite also verified Schema 14 round-trip behavior, rejection of unsupported newer schemas, evidence relationship normalization, lineage-cycle detection, type inference, and package snapshot handling.

## Controlled report-package boundary

The generated validation report package contains:

- `manifest.json`
- Standalone HTML report
- Markdown report
- Structured JSON report
- One explicitly selected image evidence binary

The selected binary matched its source fixture by SHA-256. A second unrelated evidence fixture was present in the project but absent from the report figures and package. The package did not contain the complete SENTINEL project database.

## Validation environment boundary

The available Chromium 144 environment is controlled by enterprise policy. The observed managed configuration includes:

- `URLBlocklist: ["*"]`
- Audio capture disabled
- Video capture disabled
- Printing disabled
- Print preview disabled
- Browser extension installation blocked

All ordinary local, file, data, and network origins are blocked. Focused browser tests therefore loaded the canonical application into an opaque `about:blank` document. Chromium denied native IndexedDB and Web Cryptography there, so a test-only SHA-256 bridge supplied deterministic digest results for governance transactions. Production code was not replaced or weakened.

Playwright's PDF generation interface remained available and was used to render the representative Letter report. This does not establish acceptance of the browser's interactive print dialog or every browser print engine.

Because of the managed policy, this validation does **not** claim that the complete inherited secure-origin IndexedDB, encrypted-storage, media-capture, package-reload, storage-failure, or native-print matrix reran against Release Candidate 2.

## Commands

From the release root:

```bash
python tests/static_validation.py
python tests/test_migrations_and_exports.py
python tests/report_builder_v014/static_release_checks.py
python tests/report_builder_v014/report_governance_semantic_checks.py
python tests/report_builder_v014/test_report_builder_v014.py
python tests/report_builder_v014/test_rc_browser_smoke.py
python tests/report_builder_v014/inspect_report_package.py
python tests/release_candidate_rc2/static_rc2_checks.py
python tests/release_candidate_rc2/test_accessibility_pdf_performance.py
```

On an unrestricted secure local origin, run the complete inherited matrix with:

```bash
SENTINEL_TEST_JOBS=1 SENTINEL_TEST_TIMEOUT=720 python tests/run_all.py
```

## Release gates

| Gate | Result |
|---|---|
| Canonical source identifies Version 0.15.0 Release Candidate 2 | PASS |
| Project Schema 14 | PASS |
| JavaScript syntax | PASS |
| Duplicate declared functions | PASS |
| Duplicate static element identifiers | PASS |
| Remote runtime dependencies | PASS — none found |
| Telemetry endpoints | PASS — none found |
| Schema 1 through 13 migration | PASS |
| Report composition and governance | PASS |
| Nested report-revision identifier integrity | PASS |
| Controlled selected-evidence boundary | PASS |
| Letter pagination and Page X of Y numbering | PASS |
| Focus containment and accessible audited controls | PASS |
| Large-register guardrails | PASS |
| Desktop and mobile focused browser smoke | PASS |
| Full unrestricted secure-origin inherited matrix | NOT EXECUTED IN THIS ENVIRONMENT |
| Firefox, Safari, and WebKit acceptance | OPEN |
| Physical-device media acceptance | OPEN |
| Storage and recovery fault injection | OPEN |
| Independent cryptographic and application-security review | OPEN |

## Release decision

Release Candidate 2 is ready for controlled operational acceptance and representative assessment trials. It is **not** approved as Version 1.0. The open gates are tracked in `FINAL_ACCEPTANCE_CHECKLIST.md`.
