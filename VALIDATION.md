# SENTINEL Version 0.14.0 Validation Record

Generated: 2026-08-24T20:06:10.356763+00:00

## Release decision

**Professional Report Builder 2.0 release gate: REVIEW REQUIRED**

- Focused assertions recorded: **73**
- Passed: **44**
- Failed or unmet: **29**
- Inherited regression runners executed: **1**
- Inherited runners returning success: **0**
- Inherited runners requiring review: **1**

## Critical release gate

- [ ] Build gate: Version 0.14.0
- [ ] Build gate: Schema 14
- [ ] Build gate: Report artifact
- [x] Build gate: Final issue governance
- [ ] Build gate: Revision history
- [ ] Build gate: Report package
- [x] Static: Application source exists
- [ ] Static: Application identifies Version 0.14.0
- [ ] Static: Application identifies Project Schema 14
- [x] Static: No duplicate static element identifiers
- [x] Static: No remote script or stylesheet dependencies
- [x] Static: All inline JavaScript passes node --check
- [ ] Governance semantic coverage is at least 70 percent
- [ ] Browser: Application loads
- [ ] Browser: Report Builder workspace opens
- [ ] Browser: Executive Summary visible
- [ ] Browser: Methodology visible
- [ ] Browser: Limitations visible
- [ ] Browser: Conclusion visible
- [ ] Browser: Report preview produces substantial content
- [ ] Browser: Report Builder mobile layout avoids major horizontal overflow
- [ ] Browser: No uncaught browser errors

## Professional Report Builder 2.0 validation scope

- Persistent Schema 14 report artifact and Schema 13 migration path
- Ordered built-in and custom sections
- Executive Summary, Methodology, Assessment Limitations, and Conclusion records
- Client branding, sensitivity markings, handling instructions, and approval blocks
- Evidence selection, captions, ordering, and controlled report-package boundary
- Complete appendices rather than count-only summaries
- Draft, In Review, Approved, and Final Issue lifecycle states
- Review and approval attribution and rationale
- SHA-256 issue fingerprint and Final Issue locking
- Material-project-state staleness and issued-report divergence
- New-revision workflow rather than in-place issue modification
- Standalone HTML, Markdown, JSON, browser print/PDF, and report-package output
- Desktop and mobile report workspace rendering
- JavaScript syntax, duplicate identifiers, and remote dependency checks

## Assertions requiring review

- **Static release checks — Application identifies Version 0.14.0:** 
- **Static release checks — Application identifies Project Schema 14:** 
- **Static release checks — Persistent report artifact:** 
- **Static release checks — Ordered composition:** 
- **Static release checks — Custom report sections:** 
- **Static release checks — Executive summary:** 
- **Static release checks — Methodology:** 
- **Static release checks — Branding:** 
- **Static release checks — Revision history:** 
- **Static release checks — Issue hash:** 
- **Static release checks — Report package:** 
- **Report governance semantic source checks — Report artifact is stored in project model:** 
- **Report governance semantic source checks — Report normalization preserves custom sections:** 
- **Report governance semantic source checks — New revision retains prior issue history or source reference:** 
- **Report governance semantic source checks — New revision returns to editable draft:** 
- **Report governance semantic source checks — Material project fingerprint/staleness comparison exists:** 
- **Report governance semantic source checks — Issued report divergence does not overwrite issue:** 
- **Report governance semantic source checks — Executive Summary has persistent field:** 
- **Report governance semantic source checks — Methodology has persistent field:** 
- **Report governance semantic source checks — Section order is persisted:** 
- **Report governance semantic source checks — Custom sections are editable and orderable:** 
- **Report governance semantic source checks — Report package export implementation exists:** 
- **Report governance semantic source checks — Report package uses explicit selected evidence:** 
- **Report governance semantic source checks — Report package writes manifest:** 
- **Report governance semantic source checks — Report package includes report output:** 
- **Report governance semantic source checks — Draft watermark is represented:** 
- **Report governance semantic source checks — Approval identity and rationale are represented:** 
- **Report governance semantic source checks — Issued report is not normally editable:** 
- **Report package inspection — A report package download exists:** []

## Historical runner notes

Historical regression runners are preserved as advisory results because older scripts may contain exact-version, archived-path, or previous-interface assumptions. Their complete captured output is included in `test-results/inherited_regressions.json`. Any failure that represents an application regression must be resolved before Version 1.0.

## Known validation boundaries

- Automated browser acceptance uses Chromium in this build environment.
- Browser print-to-PDF pagination varies by browser, operating system, paper size, margins, scaling, fonts, and print driver. Every final PDF still requires human visual inspection before issue.
- Report issue fingerprints provide tamper evidence inside the SENTINEL project model; they are not legally qualified digital signatures.
- Cryptographic functions and package controls have not undergone an independent external security assessment.
- Client-specific wording, legal statements, classification rules, and distribution controls remain the responsibility of the assessment organization.

