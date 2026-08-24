# SENTINEL Validation Suite

This directory contains the repeatable acceptance suite for SENTINEL Version 0.13.5 / Project Schema 13.

## Requirements

- Python 3.10 or newer
- Node.js for JavaScript syntax validation
- Python Playwright
- Chromium, Google Chrome, or a Playwright-managed Chromium build

Install the Python dependency:

```bash
python -m pip install -r tests/requirements.txt
```

When no compatible system browser is installed:

```bash
python -m playwright install chromium
```

## Run all checks

From the release root:

```bash
python tests/run_all.py
```

The runner starts a temporary local Hypertext Transfer Protocol origin, runs static validation, executes browser suites in isolated browser processes, totals reported assertions, and stops the server on completion or failure.

Optional environment variables:

- `SENTINEL_CHROMIUM` — full path to a Chromium-compatible executable
- `SENTINEL_USE_SYSTEM_CHROMIUM=1` — prefer an explicitly managed system Chromium build
- `SENTINEL_TEST_JOBS` — number of browser suites to run in parallel
- `SENTINEL_TEST_TIMEOUT` — per-suite timeout in seconds; default 300

For the most conservative execution profile:

```bash
SENTINEL_TEST_JOBS=1 SENTINEL_TEST_TIMEOUT=720 python tests/run_all.py
```

## Included suites

| Script | Focus | Assertions |
|---|---|---:|
| `static_validation.py` | Version, schema, dependencies, telemetry, syntax, identifiers, fixtures, cryptographic safeguards, direct capture, Assessment Assurance, Control Chains, remediation/retest, baseline comparison, and streamlined-shell feature presence | 31 |
| `test_core_ui.py` | Identity, storage initialization, navigation, validation, command palette, map selection, and responsive navigation | 20 |
| `test_ui_cleanup.py` | Workflow navigation, consolidated Project menu, collapsible and resizable panels, inspector behavior, dashboard guidance, scroll reset, and desktop/mobile shell geometry | 32 |
| `test_assessment_assurance.py` | Coverage outcomes and dimensions, gap rules and disclosures, completeness, sign-off, staleness, visual traceability, exports, reports, and baseline preservation | 64 |
| `test_control_chains.py` | Schema model, sequence comparison, uncertainty separation, all eight defense layers, workflow gates, lifecycle, diagrams, reports, exports, maps, traceability, baselines, assurance staleness, safety framing, and mobile layout | 43 |
| `test_remediation_retesting.py` | Immutable remediation submissions, acceptance, formal retest authorization and execution, completion locking, corrective follow-ups, independent review, finding synchronization, reports, traceability, baselines, and migration | 37 |
| `test_baseline_regression.py` | Immutable baselines, Secure Hash Algorithm 256-bit (SHA-256) verification, semantic field changes, deletion versus absence, coverage deltas, analyst dispositions, signed review, staleness, exports, reports, interface, and persistence | 35 |
| `test_field_workflow.py` | Authorized test start, one-active-test rule, completion, abort, status transitions, and timeline | 15 |
| `test_evidence_integrity.py` | Metadata history, immutable originals, verification, and integrity state | 9 |
| `test_evidence_organization.py` | Search, filters, grouping, layouts, bulk updates, archive state, and Photo Log behavior | 15 |
| `test_media_previews.py` | Text, audio, video, and Portable Document Format previews and metadata | 9 |
| `test_editor_tools.py` | Every image-editor operation, undo, crop, rotation, derivative creation, and source preservation | 27 |
| `test_evidence_workstation.py` | End-to-end evidence ingestion, preview, custody, relationships, derivation, comparison, Photo Log, and reporting | 32 |
| `test_package_persistence.py` | Reload, Save As Copy, binary copying, plaintext package export and import, hashes, and thumbnail regeneration | 17 |
| `test_secure_storage.py` | Protected Indexed Database stores, lock/reload/unlock, wrong-passphrase rejection, passphrase rotation, decryption, screen-lock-only reload, and hash preservation | 21 |
| `test_encrypted_packages.py` | Encrypted package envelope, metadata confidentiality, passphrase authentication, download, clean-profile import, and binary verification | 14 |
| `test_capture_recovery.py` | Encrypted pending-capture staging, lock/reload recovery, immutable commit, provenance, timeline, and explicit discard | 12 |
| `test_direct_media_capture.py` | Live photograph, video, and audio capture with deterministic fake devices, recording feedback, queue staging, and evidence commit | 11 |
| `test_security_ui.py` | Classification banner, Security & Storage workspace, policy persistence, capture controls, storage estimate, protected previews, and mobile containment | 17 |
| `test_reports.py` | Photo Log, assurance sign-off, report readiness, Hypertext Markup Language and Markdown output, markings, images, version, and schema | 15 |
| `test_migrations_and_exports.py` | Schemas 1–12, Schema 13 round trip, newer-schema rejection, legacy normalization, cycles, and package snapshots | 47 |
| `test_mobile_evidence.py` | Mobile Evidence Vault, Photo Log, Evidence Workstation, modal stacking, and navigation | 12 |
| **Total** | **31 static and 504 browser assertions across 21 browser suites** | **535** |

## Fixtures and assets

`fixtures/` contains representative projects from every previously published schema:

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

`assets/` contains small local photograph, text, audio, video, and Portable Document Format samples used for real browser ingestion and preview testing.

The direct-media suite uses Chromium’s deterministic fake camera and microphone devices. This validates the browser capture path without claiming acceptance of every physical camera, microphone, codec, mobile operating system, or device permission policy.

## Interface cleanup suite

`test_ui_cleanup.py` validates the Version 0.13.5 shell rather than relying on screenshots alone. It verifies the four-row application grid, classification/workspace separation, desktop-only and mobile-only controls, the consolidated Project menu, workflow navigation groups, sidebar collapse and persisted resizing, automatic desktop Traceability Inspector behavior, scroll reset between destinations, lifecycle guidance on the Dashboard, compact mobile footer, absence of page-level horizontal overflow, and mobile drawer operation.

The cleanup also extended existing tests so Save As Copy and package export are exercised through the consolidated Project menu, and mobile backdrop interactions target the actual area outside the navigation drawer.

## Baseline Comparison and Regression suite

`test_baseline_regression.py` creates an initial baseline and a changed follow-up baseline. It verifies immutable SHA-256 sealing, integrity verification, tamper detection, severity and test-result regressions, remediation improvement, authorization and map review items, record addition, deliberate deletion with a tombstone, unexplained later absence, coverage deltas, per-change analyst disposition, final review SHA-256 verification, review staleness, JavaScript Object Notation (JSON), Comma-Separated Values (CSV), and Hypertext Markup Language (HTML) exports, report integration, interface rendering, and persistence after browser reload.

The suite deliberately keeps automatic impact suggestions separate from the signed analyst record. Every regression and review item must receive a disposition, rationale, and accountable owner before review sign-off can succeed.

## Control Chains suite

`test_control_chains.py` creates a representative defensive architecture with expected and observed paths. It verifies ordered comparison, duplicate and reordered records, all eight defense layers, evidence-supported control states, separate evidence limitations, lifecycle review, material-change invalidation, map highlighting, traceability, baseline comparison, report output, Scalable Vector Graphics (SVG) and JSON exports, mobile layout, and safety language.

The test intentionally treats control-interaction candidates as analyst prompts. It verifies that insufficient evidence is not converted into control failure and that the application does not produce bypass instructions.

## Remediation and Formal Retesting suite

`test_remediation_retesting.py` builds a complete recommendation-to-retest workflow. It verifies immutable finding and recommendation snapshots, submission and acceptance attestations, governed retest planning and authorization, completion fingerprints, independent-review separation, finding closure and reopening, corrective follow-up records, evidence relationships, reports, traceability, baseline comparison, and migration.

The suite confirms that submitted remediation records, authorized retest plans, and completed or reviewed retests cannot be silently rewritten. Corrections must be represented by explicitly linked follow-up records so the historical assessment record remains intact.

## Browser policy note

Enterprise policies that block every local origin can prevent the temporary test server from loading. Run the suite in a normal test profile or permit the temporary `127.0.0.1` origin. The application itself does not require internet access.

## Failure artifacts

Browser suites attempt to write a screenshot beneath the suite-specific temporary directory when an assertion fails. Test output identifies the failing assertion and exits with a nonzero status.
