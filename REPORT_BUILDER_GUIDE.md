# SENTINEL Professional Report Builder 2.0 Guide

This guide covers the governed reporting workflow in SENTINEL Version 0.15.0 Release Candidate 1 / Project Schema 14.

## 1. Prepare the assessment record

Before composing a final report, confirm that the project contains the assessment records needed to support its conclusions:

- Scope and authorization
- Rules of Engagement
- Site hierarchy and assessed locations
- Security controls and test cases
- Test events and observations
- Verified evidence or documented evidence limitations
- Validated findings and positive observations
- Assessment Assurance review and current sign-off
- Remediation and formal retest records where applicable
- Reviewed baseline comparisons where applicable

Use **Assessment Assurance** to identify unsupported findings, tests without evidence, untested controls, weak location coverage, unresolved integrity problems, and stale sign-off records.

## 2. Open the Report Builder

Open **Report** from the Closeout navigation group. The Professional Report Builder 2.0 is organized into five workspaces:

1. **Composition** — identity, branding, narrative, section order, and custom sections
2. **Evidence** — report-specific evidence selection and captions
3. **Appendices** — complete appendix inclusion controls
4. **Preview & Export** — governed output generation
5. **Governance** — review, approval, Final Issue, divergence, and revision history

## 3. Compose the report

### Identity and document controls

Set the report title, subtitle, revision, client, assessed site, assessment dates, sensitivity marking, handling instructions, header, footer, and client branding.

The report’s document controls are revision-specific. A later report revision may use updated branding or markings without rewriting an earlier Final Issue.

### Core narrative

Complete the dedicated narrative records for:

- Executive Summary
- Scope and Authorization
- Methodology
- Site Overview
- Security Architecture
- Assessment Limitations
- Conclusion

The Executive Summary should communicate overall posture, major strengths, major weaknesses, and priority actions without replacing the detailed findings.

The Methodology should describe what was assessed, how coverage was established, what sampling was used, and how evidence was evaluated. Do not imply complete coverage when the assessment used sampling.

The Assessment Limitations section should disclose unavailable areas, unavailable personnel, prohibited methods, timing restrictions, equipment failures, evidence limitations, and other conditions that materially constrain conclusions.

### Built-in sections

Each built-in section can be included or excluded and moved within the report order. Excluding a section from one revision does not delete the underlying project records.

### Custom sections

Create custom sections for client-specific material such as Management Response, Facility Context, Corrective Action Plan, Distribution Statement, or Contractual Notes.

Custom sections persist through autosave, project packages, migration, revision creation, review, approval, and Final Issue.

## 4. Select report evidence

The Evidence workspace lists project evidence that may be deliberately included in the report.

For each selected item, set:

- Inclusion state
- Destination section
- Related finding where applicable
- Report-specific caption
- Display order

Prefer report-safe derived evidence when annotation or redaction is required. SENTINEL preserves the immutable original separately.

Confirm that selected evidence has an acceptable integrity state and that the caption does not disclose information outside the intended distribution boundary.

Unselected evidence remains in the project and is excluded from the controlled report package.

## 5. Select appendices

Appendices are controlled independently for each report revision. Available appendices include:

- Test Log
- Observation Register
- Evidence Index
- Photo Log
- Coverage Matrix
- Rules of Engagement
- Daily Field Logs
- Remediation Submissions
- Formal Retest Register
- Baseline Comparisons
- Control Chains
- Assumptions Register
- Issues Register
- Interaction Log
- Outstanding Questions

Review appendix sensitivity carefully. A report may be suitable for broader distribution while a complete Test Log, Rules of Engagement appendix, or Interaction Log is not.

## 6. Preview the report

Use the interactive preview before governance submission.

Check:

- Title, client, site, dates, revision, and markings
- Section order and inclusion
- Heading hierarchy
- Finding severity and status
- Evidence images and captions
- Positive observations
- Coverage and limitations
- Control Chain and defense-layer figures
- Remediation and retest state
- Baseline comparison conclusions
- Appendix contents
- Prepared-by, reviewed-by, and approval blocks

Draft previews are clearly marked as Draft and must not be mistaken for Final Issue.

## 7. Submit for review

In Governance, record the submitter and submit the Draft revision for review.

The reviewer should verify:

- Conclusions are traceable to assessment records.
- Evidence supports the stated findings.
- Limitations are explicit.
- Severity, confidence, and remediation language are defensible.
- Report evidence is appropriate for the distribution audience.
- Appendices do not disclose unnecessary sensitive information.
- Assessment Assurance is current.
- Retest and baseline statements match their governed records.

A report returned to Draft requires reviewer attribution and rationale. The return becomes part of the revision history.

## 8. Approve the report

Approval requires an identified approval authority and approval rationale. Approval is separate from review.

Approval records the approved material state. Material changes after approval require the report to return through governance rather than silently retaining approval.

## 9. Create Final Issue

Before issuing, enter the Final Issue number, issuing authority, and distribution note as required.

SENTINEL performs Final Issue atomically:

1. Confirms that the revision is Approved.
2. Confirms the approval fingerprint is valid.
3. Applies issue metadata to a transaction candidate.
4. Captures the exact issued report and assessment snapshot.
5. Calculates the Secure Hash Algorithm 256-bit (SHA-256) Final Issue fingerprint.
6. Commits the locked Final Issue only after every step succeeds.

A failed seal or validation operation does not leave a partially issued report.

After Final Issue, the revision is read-only. Its issue metadata, snapshot, fingerprint, outputs, and history remain preserved.

## 10. Handle post-issue project changes

When the live project materially changes after Final Issue, SENTINEL displays **LIVE PROJECT DIVERGED**.

The warning means the issued report no longer represents the current live project. It does not modify the issued snapshot or fingerprint.

Create a new revision to report later evidence, remediation, retest, baseline, authorization, finding, or scope changes. The new revision begins as Draft and preserves its relationship to the prior issue.

## 11. Export outputs

### Standalone Hypertext Markup Language

Use for an offline, browser-readable report with embedded selected images.

### Markdown

Use for portable text review, controlled editing outside SENTINEL, or downstream publication workflows. External edits are not governed by the SENTINEL issue record unless reintroduced as a new project revision.

### Structured JavaScript Object Notation

Use for machine-readable exchange, archival inspection, or downstream tooling. It includes the governed report structure and explicit evidence selections.

### Portable Document Format

Use browser printing to create a PDF. Review every final PDF visually. Confirm page breaks, headers, footers, markings, captions, tables, signature blocks, and appendix pagination.

### Controlled report package

The report package ZIP contains:

- Standalone HTML
- Markdown
- Structured JSON
- Package manifest
- Exactly the evidence selected for report distribution

The manifest records file paths, sizes, and SHA-256 values. The package is a distribution artifact, not a complete SENTINEL backup.

## 12. Preserve the project

After Final Issue, create or export a complete SENTINEL project package separately. The project package preserves the working assessment record, including material intentionally excluded from the report package.

Where project sensitivity requires it, use an encrypted project package and preserve the passphrase through an approved external process. SENTINEL cannot recover a forgotten passphrase.

## Final PDF issue checklist

- [ ] Correct report title, client, site, dates, issue number, and revision
- [ ] Correct sensitivity marking and handling instructions
- [ ] No Draft watermark
- [ ] Correct prepared-by, reviewed-by, approval, and issuing-authority blocks
- [ ] Executive Summary matches detailed findings
- [ ] Scope, methodology, and limitations are explicit
- [ ] Findings are complete and supported
- [ ] Evidence images are legible, correctly captioned, and properly redacted
- [ ] Positive observations are separated from findings
- [ ] Coverage claims do not exceed tested scope
- [ ] Remediation and retest statements match governed records
- [ ] Baseline comparison statements match reviewed comparisons
- [ ] Appendices contain only intended records
- [ ] Headers, footers, page numbers, tables, and page breaks are acceptable
- [ ] Final Issue fingerprint and issue history are recorded in SENTINEL
- [ ] Controlled report package contains only explicitly selected evidence
- [ ] Complete project backup is stored separately
