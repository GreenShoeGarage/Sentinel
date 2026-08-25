# SENTINEL Final Acceptance Checklist

**Target:** Version 1.0 controlled operational release  
**Starting build:** Version 0.15.0 Release Candidate 2 / Project Schema 14

Complete each gate on the intended release bytes. Record the browser, operating system, hardware, test date, analyst, and evidence location for every acceptance run.

## Release reconciliation

- [ ] The release ZIP, loose `index.html`, version file, documentation, manifest, and checksum identify the same application version and schema.
- [ ] The release manifest verifies every declared file size and Secure Hash Algorithm 256-bit (SHA-256) value.
- [ ] The application source in the ZIP is byte-for-byte identical to the validated loose source.
- [ ] The ZIP passes archive-integrity testing.
- [ ] No stale, duplicate, backup, or superseded application source is included.

## Secure-origin regression matrix

- [ ] Run `tests/run_all.py` from an unrestricted local Hypertext Transfer Protocol (HTTP) or Hypertext Transfer Protocol Secure (HTTPS) origin.
- [ ] All inherited static and browser suites pass against the release bytes.
- [ ] Indexed Database persistence survives browser close and restart.
- [ ] Evidence and map binaries survive save, reload, project copy, export, import, and recovery.
- [ ] Native Web Cryptography operations pass without a test bridge.
- [ ] Plain and encrypted project-package round trips pass in clean browser profiles.

## Browser acceptance

- [ ] Current Chromium or Google Chrome acceptance passes.
- [ ] Current Firefox acceptance passes.
- [ ] Current Safari acceptance passes on macOS.
- [ ] WebKit acceptance passes on the intended test platform.
- [ ] Browser-specific limitations are documented in the supported-browser matrix.

## Field-device and media acceptance

- [ ] Intended laptop workflow passes.
- [ ] Intended tablet workflow passes in portrait and landscape orientations.
- [ ] Intended phone workflow passes in portrait and landscape orientations.
- [ ] Front and rear camera photograph capture passes where supported.
- [ ] Video capture and duration controls pass where supported.
- [ ] Audio-note capture passes where supported.
- [ ] Permission denial, revocation, interruption, and device-switch behavior are understandable and recoverable.
- [ ] Pending captures survive reload and can be previewed, committed, downloaded, or discarded.
- [ ] Representative codecs and large media files are accepted or rejected with clear guidance.

## Storage, recovery, and fault injection

- [ ] Browser quota is measured on every target browser and device class.
- [ ] The 75-percent and 90-percent storage warnings behave correctly.
- [ ] Emergency Export succeeds under constrained storage.
- [ ] Interrupted autosave does not silently lose the last known good project state.
- [ ] Interrupted project import leaves the existing project recoverable.
- [ ] Interrupted encrypted-package export is reported as incomplete.
- [ ] Corrupt project packages are rejected without overwriting the active project.
- [ ] Corrupt recovery checkpoints are rejected and earlier valid checkpoints remain available.
- [ ] Missing and mismatched evidence binaries are clearly reported.
- [ ] Save As Copy preserves intended binaries while generating a separate project identity.

## Security and privacy

- [ ] Independent review covers local encryption, key wrapping, passphrase handling, package encryption, and authenticated metadata.
- [ ] Independent application-security testing covers input handling, imported packages, document rendering, media previews, and browser storage.
- [ ] The privacy and threat model documents endpoint compromise, browser-extension compromise, unlocked sessions, backups, screen capture, memory exposure, and deletion limitations.
- [ ] Classification, handling, export acknowledgement, and auto-lock behavior are accepted by the intended security authority.
- [ ] Passphrase-loss procedures and approved external passphrase custody are documented.
- [ ] No telemetry, analytics, remote runtime dependency, or hidden network call is present.

## Accessibility and usability

- [ ] Complete keyboard-only navigation passes across all Easy and Advanced workspaces.
- [ ] Command palette, navigation drawer, Inspector, and every modal contain and restore focus correctly.
- [ ] Screen-reader acceptance passes with at least one Windows and one Apple assistive-technology combination.
- [ ] Form labels, validation messages, status changes, tables, graphs, and report-governance controls are announced meaningfully.
- [ ] Color contrast and non-color status cues pass review.
- [ ] Reduced-motion behavior is accepted.
- [ ] Touch targets and mobile navigation are accepted on representative physical devices.
- [ ] Terminology and workflow are reviewed by an experienced physical security assessment practitioner.

## Performance and scale

- [ ] Representative projects below 5,000 material records remain responsive on target laptops and tablets.
- [ ] The 500-row interactive limit is clearly disclosed and does not truncate data, reports, or exports.
- [ ] Large Evidence Vaults with representative photographs, videos, audio, Portable Document Format files, and floor plans are tested.
- [ ] Hashing, derivation, package export, package import, and report generation are profiled with representative large binaries.
- [ ] Memory pressure and browser termination behavior are documented.
- [ ] A practical supported project-size and evidence-size envelope is published.

## Professional reporting

- [ ] Report composition, selected evidence, appendices, review, approval, Final Issue, and new-revision workflows pass on the target browser matrix.
- [ ] Issued revisions remain immutable and display live-project divergence correctly.
- [ ] Report-package exports contain exactly the intended derived evidence and exclude unrelated project material.
- [ ] Representative United States Letter PDFs pass visual issue review.
- [ ] Representative A4 PDFs pass visual issue review.
- [ ] Running markings and Page X of Y numbering are correct on supported print engines.
- [ ] Headers, footers, page breaks, tables, captions, redactions, signature blocks, and appendices are visually accepted.
- [ ] Draft watermarking is present only when intended.
- [ ] Final Issue fingerprints and issue histories are preserved after save, reload, package transfer, and recovery.
- [ ] Every final client PDF receives a documented visual issue review before distribution.

## Migration and baseline integrity

- [ ] Every published project schema migrates to Schema 14 in the unrestricted matrix.
- [ ] Unsupported newer schemas are rejected without destructive guessing.
- [ ] Migration checkpoints are created before material conversion.
- [ ] Baseline seals and comparison review hashes verify after save, reload, package transfer, and recovery.
- [ ] Original findings, evidence, remediation submissions, retests, and issued reports remain historically intact after migration.

## Version 1.0 release decision

- [ ] No known blocking field workflow remains.
- [ ] No known data-loss or evidence-integrity defect remains.
- [ ] No known reporting-governance or report-package boundary defect remains.
- [ ] All supported browser and device gates are recorded.
- [ ] All accepted limitations are documented in the README and release notes.
- [ ] The release authority approves Version 1.0 for controlled operational use.
