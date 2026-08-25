# SENTINEL Version 0.15.0 Release Candidate 1 Validation Record

**Project schema:** 14  
**Validation date:** August 24, 2026  
**Release decision:** Release Candidate — Professional Report Builder 2.0 implementation complete; final cross-browser, physical-device, secure-origin, storage-failure, and external security acceptance remains before Version 1.0.

## Release reconciliation

The final review determined that the earlier archive labeled Version 0.14.0 was not a valid canonical Schema 14 release. Its `index.html` still identified Version 0.13.5 / Project Schema 13, while its validation artifacts showed unpassed Report Builder 2.0 gates.

Version 0.15.0 Release Candidate 1 supersedes that archive. This release was built and validated from one canonical source tree whose application, documentation, schema, version, test results, and manifest agree.

## Executed validation matrix

| Suite | Assertions | Result |
|---|---:|---|
| Full-application static validation | 31 | PASS |
| Schema migration and export validation | 50 | PASS |
| Report Builder static implementation checks | 29 | PASS |
| Report-governance semantic source checks | 43 | PASS |
| Professional Report Builder browser acceptance | 59 | PASS |
| Broad release-candidate browser smoke | 23 | PASS |
| Controlled report-package inspection | 8 | PASS |
| **Executed total** | **243** | **PASS** |

These are executed assertions across seven suites. Some suites deliberately examine the same critical surface through different methods; the total is a count of executed checks, not a claim that every check is unique.

## Report Builder acceptance coverage

The focused report matrix verified:

- Persistent Schema 14 report artifact
- Report identity, branding, markings, narrative, ordered built-in sections, and custom sections
- Custom-section preservation through normalization and revision creation
- Explicit selected-evidence records, captions, placement, and ordering
- Full appendix controls
- Preview rendering
- Draft, In Review, Approved, and Final Issue lifecycle
- Review and approval attribution and rationale
- Approval-fingerprint verification
- Transactionally atomic Final Issue behavior
- Secure Hash Algorithm 256-bit (SHA-256) issue seal
- Read-only issued revision and immutable issued snapshot
- Live-project divergence detection without rewriting the issued artifact
- New Draft revision linked to the prior issue
- Standalone Hypertext Markup Language (HTML), Markdown, and structured JavaScript Object Notation (JSON)
- Print-to-Portable Document Format (PDF) media rules
- Standalone HTML image decoding and page-level overflow
- Controlled report-package ZIP creation
- Package manifest and file-hash verification
- Inclusion of exactly the explicitly selected evidence binary
- Exclusion of unrelated project evidence
- Mobile Report Builder containment
- Absence of uncaught material browser errors

The final Professional Report Builder browser suite passed **59 of 59** assertions.

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

Every fixture reached Schema 14 and passed the post-migration project audit. The suite also verified Schema 14 round-trip behavior, rejection of unsupported newer schemas, legacy evidence relationship normalization, lineage-cycle detection, evidence type inference, and package snapshot handling.

## Broad application smoke coverage

The release-candidate browser smoke suite verified:

- Version and Schema identity
- Project audit execution
- All 21 Advanced Mode destinations
- Command palette
- Consolidated Project menu
- Sidebar collapse without workspace loss
- Professional Report Builder presence
- Desktop rendering
- Mobile navigation drawer
- Mobile horizontal containment
- Compact mobile footer
- No uncaught browser exceptions
- No material console errors

## Controlled package boundary

The generated validation report package contains:

- `manifest.json`
- Standalone HTML report
- Markdown report
- Structured JSON report
- One explicitly selected image evidence binary

The package manifest identifies the report and revision, lists selected evidence, and records output hashes. The selected binary matched its source fixture by SHA-256. A second unrelated evidence fixture was present in the project but absent from both the report figures and report package.

## Validation environment boundary

The available Chromium 144 environment is controlled by enterprise policy. Its managed configuration includes:

- `URLBlocklist: ["*"]`
- Audio capture disabled
- Video capture disabled
- Printing disabled
- Browser extension installation disabled

All ordinary local, file, data, and network origins are blocked. The only usable browser document context was `about:blank`, where Chromium denies IndexedDB and native Web Cryptography operations.

Focused Report Builder and user-interface browser tests therefore loaded the canonical application source into `about:blank`. A test-only SHA-256 bridge supplied deterministic digest results for governance transactions. Production source continues to use native Web Cryptography; the bridge is exposed only through the internal test interface used by the acceptance fixture.

Because the managed host prevents a normal secure origin, this validation does **not** claim that the complete inherited IndexedDB, encrypted-storage, direct-camera, microphone, video, package-reload, and secure-origin browser matrix reran against Version 0.15.0 Release Candidate 1.

The full inherited suite remains included under `tests/` and should be run on an unrestricted local Hypertext Transfer Protocol origin before Version 1.0.

## Validation commands

From the release root:

```bash
python tests/static_validation.py
python tests/test_migrations_and_exports.py
python tests/report_builder_v014/static_release_checks.py
python tests/report_builder_v014/report_governance_semantic_checks.py
python tests/report_builder_v014/test_report_builder_v014.py
python tests/report_builder_v014/test_rc_browser_smoke.py
python tests/report_builder_v014/inspect_report_package.py
```

On an unrestricted test host, run the inherited secure-origin matrix with:

```bash
SENTINEL_TEST_JOBS=1 SENTINEL_TEST_TIMEOUT=720 python tests/run_all.py
```

## Release gates

| Gate | Status |
|---|---|
| Canonical source identifies Version 0.15.0 Release Candidate 1 | PASS |
| Canonical source identifies Project Schema 14 | PASS |
| Complete JavaScript syntax validation | PASS |
| No duplicate declared functions | PASS |
| No duplicate static element identifiers | PASS |
| No remote runtime dependencies | PASS |
| No telemetry endpoints | PASS |
| Schema 1–13 migration to Schema 14 | PASS |
| Persistent governed report artifact | PASS |
| Ordered and custom composition | PASS |
| Explicit selected-evidence boundary | PASS |
| Review and approval governance | PASS |
| Atomic Final Issue and SHA-256 sealing | PASS |
| Final Issue immutability | PASS |
| Project-divergence detection | PASS |
| New revision workflow | PASS |
| HTML, Markdown, JSON, print, and report-package outputs | PASS |
| Package manifest and selected-binary hash verification | PASS |
| Broad desktop and mobile smoke | PASS |
| Full unrestricted secure-origin inherited matrix | NOT RUN IN THIS ENVIRONMENT |
| Firefox, Safari, and WebKit matrix | PENDING |
| Physical-device capture matrix | PENDING |
| Independent cryptographic/security review | PENDING |
| Representative final PDF visual issue review | PENDING |

## Release conclusion

No known report-governance blocker remains in the executed release-candidate matrix. The Professional Report Builder 2.0 implementation is complete enough for controlled evaluation.

The release should remain a Release Candidate until the unrestricted inherited browser suite, target-browser and physical-device acceptance, storage and recovery fault drills, security review, and representative final PDF issue review are complete.
