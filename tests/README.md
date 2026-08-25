# SENTINEL Validation Suite

This directory contains the repeatable validation suite for SENTINEL Version 0.15.0 Release Candidate 2 / Project Schema 14.

## Requirements

- Python 3.10 or newer
- Node.js for JavaScript syntax validation
- Python Playwright
- Chromium, Google Chrome, or a Playwright-managed Chromium build
- PyMuPDF for focused Portable Document Format acceptance

Install dependencies:

```bash
python -m pip install -r tests/requirements.txt
python -m playwright install chromium
```

## Full inherited secure-origin matrix

From the release root:

```bash
SENTINEL_TEST_JOBS=1 SENTINEL_TEST_TIMEOUT=720 python tests/run_all.py
```

The runner starts a temporary local Hypertext Transfer Protocol origin, executes static validation, and runs inherited browser suites in isolated browser processes.

Optional environment variables:

- `SENTINEL_CHROMIUM` — full path to a Chromium-compatible executable
- `SENTINEL_USE_SYSTEM_CHROMIUM=1` — prefer an explicitly managed system Chromium build
- `SENTINEL_TEST_JOBS` — browser-suite parallelism
- `SENTINEL_TEST_TIMEOUT` — per-suite timeout in seconds

The full matrix requires a browser profile that permits the temporary `127.0.0.1` origin, Indexed Database, Web Cryptography, downloads, and tested media permissions.

## Release Candidate 2 focused matrix

Run the nine focused suites with:

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

The final focused run passes **288 assertions** across these nine suites.

The two Release Candidate 2 suites specifically verify:

- Letter-safe report-cover geometry
- Paged-media running headers and Page X of Y numbering
- Absence of Page 0 and accidental blank report pages
- Programmatic names for audited form controls
- Command-palette and modal focus containment and restoration
- Reduced-motion and mobile touch-target rules
- 500-row interactive register disclosure without data truncation
- 5,000-record large-project detection
- Representative Letter PDF generation and inspection

## Inherited suites

The inherited matrix covers the application shell, user-interface cleanup, authorization, field workflow, direct capture, capture recovery, evidence integrity and organization, media previews, image-editor tools, project persistence, secure local storage, encrypted packages, Assessment Assurance, Control Chains, remediation and formal retesting, baseline comparison, reporting, migration, and mobile behavior.

`test_migrations_and_exports.py` contains 50 assertions and includes fixtures from Schemas 1 through 13 plus a Schema 14 round trip.

## Fixtures and assets

`fixtures/` contains representative projects from every previously published project schema through Schema 13.

`assets/` contains local image, unrelated-image, text, audio, video, and PDF samples. The two distinct image fixtures verify that a controlled report package contains the selected image and excludes unrelated evidence.

The direct-media suite uses Chromium deterministic fake camera and microphone devices. This validates browser capture pathways without claiming acceptance of every physical device, codec, mobile operating system, or permission policy.

## Managed-browser policy note

Enterprise policy can block local origins or disable Indexed Database, media capture, printing, and downloads. Run the full matrix in an unrestricted test profile. The focused report browser fixtures can exercise composition and governance in an opaque document, but they do not replace the full secure-origin persistence and capture matrix.

## Failure artifacts

Browser suites write result files and attempt to capture screenshots beneath `test-results/`. A failed assertion exits with a nonzero status.
