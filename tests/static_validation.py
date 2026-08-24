"""Static release checks that do not require a browser."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
source = INDEX.read_text(encoding="utf-8")
results: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    results.append(name)
    print("PASS", name, detail)


check("release-version", "APP_VERSION='0.13.5'" in source)
check("release-schema", "SCHEMA_VERSION=13" in source)
check("no-remote-runtime-dependencies", not re.search(r"(?:src|href)=[\"']https?://", source, re.I))
check("no-telemetry-endpoints", not re.search(r"google-analytics|googletagmanager|segment\.com|sentry\.io|mixpanel", source, re.I))
check("exif-gps-coordinates-not-surfaced", "GPSPresent" in source and "GPSLatitude" not in source and "GPSLongitude" not in source and "GPSAltitude" not in source)
check("authenticated-local-encryption-present", all(term in source for term in ["AES-GCM", "PBKDF2", "secureProjects", "secureEvidence", "secureAssets", "secureCheckpoints"]))
check("encrypted-package-envelope-present", all(term in source for term in ["SENTINEL_ENCRYPTED_PACKAGE", "encryptPackageManifest", "decryptEncryptedPackage"]))
check("recoverable-capture-queue-present", all(term in source for term in ["captureQueue", "secureCaptureQueue", "stageCapture", "commitPendingCapture"]))
check("direct-media-capture-present", all(term in source for term in ["getUserMedia", "MediaRecorder", "startPhotoCapture", "startMediaCapture"]))
check("storage-and-lock-safeguards-present", all(term in source for term in ["navigator.storage.estimate", "lockWorkspace", "protected-preview", "Logical deletion"]))
check("control-chain-workspace-present", all(term in source for term in ["Control Chains & Defense in Depth", "expectedPath", "observedPath", "combinedWeaknessAnalysis", "defensePortfolioSummary"]))
check("control-chain-reporting-present", all(term in source for term in ["controlChainStandaloneHtml", "controlChainMarkdown", "Export Path SVG", "Export Layers SVG"]))
check("control-chain-safety-language-present", "not attack instructions" in source and "not provide bypass instructions" in source)
check("remediation-retest-workspace-present", all(term in source for term in ["Remediation & Formal Retesting", "Remediation Submissions", "Independent Review", "openRetestReview"]))
check("immutable-retest-records-present", all(term in source for term in ["IMMUTABLE COMPLETED RETEST", "completionSha256", "retestExecutionLocked", "Create Corrective / Follow-up Retest"]))
check("retest-traceability-and-reporting-present", all(term in source for term in ["findingSnapshotForRetest", "remediationSnapshotForRetest", "retestReportHtml", "retestMarkdown"]))
check("semantic-baseline-comparison-present", all(term in source for term in ["semanticBaselineDiff", "ABSENT_LATER", "recordTombstones", "baselineCoverageMetrics"]))
check("immutable-baseline-hashes-present", all(term in source for term in ["snapshotHash", "sealBaseline", "verifyBaselineIntegrity", "SHA-256"]))
check("baseline-review-workflow-present", all(term in source for term in ["baselineComparisons", "finalizeBaselineComparison", "reviewSha256", "REVIEW CHANGED"]))
check("baseline-reporting-and-exports-present", all(term in source for term in ["baselineComparisonReportSectionHtml", "baselineComparisonReportMarkdown", "baselineCsv", "baselineComparisonHtmlDocument"]))
check("streamlined-shell-present", all(term in source for term in ["project-menu", "sidebarProjectMenuBtn", "inspectorToggleBtn", "sidebarResize", "inspectorResize"]))
check("workflow-navigation-present", all(term in source for term in [">Workspace<", ">Fieldwork<", ">Analysis<", ">Closeout<", ">Administration<"]))
check("responsive-shell-fix-present", "grid-template-rows:auto auto minmax(0,1fr) auto" in source and ".mobile-menu-btn{display:none}" in source)
check("dashboard-guidance-present", all(term in source for term in ["workflow-strip", "dashNextAction", "SCOPE", "RETEST"]))

scripts = re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>", source, re.I)
check("single-inline-script", len(scripts) == 1, len(scripts))
with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
    handle.write(scripts[0])
    js_path = Path(handle.name)
try:
    node = subprocess.run(["node", "--check", str(js_path)], text=True, capture_output=True)
    check("javascript-syntax", node.returncode == 0, node.stderr)
finally:
    js_path.unlink(missing_ok=True)

functions = re.findall(r"(?:^|\n)\s*(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", scripts[0])
duplicates = sorted({name for name in functions if functions.count(name) > 1})
check("declared-function-uniqueness", not duplicates, duplicates)
check("substantial-function-coverage", len(set(functions)) >= 400, len(set(functions)))

class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: list[str] = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id" and value and "${" not in value:
                self.ids.append(value)

# Parse only markup before the application script; modal templates are JavaScript strings.
parser = IdParser()
parser.feed(source.split("<script>", 1)[0])
id_duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
check("static-element-id-uniqueness", not id_duplicates, id_duplicates)

fixture_paths = sorted((ROOT / "tests" / "fixtures").glob("schema*.json"))
check("migration-fixtures-present", len(fixture_paths) == 12, len(fixture_paths))
asset_paths = sorted((ROOT / "tests" / "assets").glob("sample_*"))
check("media-test-assets-present", len(asset_paths) >= 5, [path.name for path in asset_paths])

print(f"ALL PASS {len(results)} assertions")
print(f"ASSERTIONS={len(results)}")
