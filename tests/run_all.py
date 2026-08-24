"""Start a local origin and run the complete SENTINEL v0.13.5 validation suite."""
from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import urlopen

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent
STATIC_SCRIPT = "static_validation.py"
BROWSER_SCRIPTS = [
    "test_core_ui.py",
    "test_ui_cleanup.py",
    "test_assessment_assurance.py",
    "test_control_chains.py",
    "test_remediation_retesting.py",
    "test_baseline_regression.py",
    "test_field_workflow.py",
    "test_evidence_integrity.py",
    "test_evidence_organization.py",
    "test_media_previews.py",
    "test_editor_tools.py",
    "test_evidence_workstation.py",
    "test_package_persistence.py",
    "test_secure_storage.py",
    "test_encrypted_packages.py",
    "test_capture_recovery.py",
    "test_direct_media_capture.py",
    "test_security_ui.py",
    "test_reports.py",
    "test_migrations_and_exports.py",
    "test_mobile_evidence.py",
]
SCRIPT_TIMEOUT = int(os.environ.get("SENTINEL_TEST_TIMEOUT", "300"))
DEFAULT_JOBS = min(2, max(1, os.cpu_count() or 1))
JOBS = max(1, int(os.environ.get("SENTINEL_TEST_JOBS", str(DEFAULT_JOBS))))


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def run_script(script: str, env: dict[str, str], tmp_root: Path) -> tuple[str, int, str]:
    script_tmp = tmp_root / Path(script).stem
    script_tmp.mkdir(parents=True, exist_ok=True)
    script_env = env.copy()
    script_env["SENTINEL_TEST_TMP"] = str(script_tmp)
    try:
        completed = subprocess.run(
            [sys.executable, str(TEST_DIR / script)],
            cwd=str(TEST_DIR),
            env=script_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=SCRIPT_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        return script, 124, output + f"\nFAILED: {script} exceeded the {SCRIPT_TIMEOUT}-second test limit.\n"
    return script, completed.returncode, completed.stdout


def assertion_count(output: str, script: str) -> int:
    matches = re.findall(r"ASSERTIONS=(\d+)", output)
    if not matches:
        raise RuntimeError(f"{script} did not report an assertion count")
    return int(matches[-1])


port = free_port()
url = f"http://127.0.0.1:{port}/index.html"
server = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", str(ROOT)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
try:
    for _ in range(100):
        try:
            with urlopen(url, timeout=0.25) as response:
                if response.status == 200:
                    break
        except Exception:
            time.sleep(0.1)
    else:
        raise RuntimeError("Local validation server did not start")

    env = os.environ.copy()
    env["SENTINEL_URL"] = url
    tmp_root = Path(tempfile.mkdtemp(prefix="sentinel-validation-"))

    print(f"\n=== {STATIC_SCRIPT} ===", flush=True)
    static_script, static_code, static_output = run_script(STATIC_SCRIPT, env, tmp_root)
    print(static_output, end="")
    if static_code:
        raise SystemExit(static_code)
    total = assertion_count(static_output, static_script)

    print(f"\nRunning {len(BROWSER_SCRIPTS)} browser suites with {JOBS} parallel job(s).", flush=True)
    results: dict[str, tuple[int, str]] = {}
    with ThreadPoolExecutor(max_workers=JOBS) as executor:
        futures = {executor.submit(run_script, script, env, tmp_root): script for script in BROWSER_SCRIPTS}
        for future in as_completed(futures):
            script, code, output = future.result()
            results[script] = (code, output)
            print(f"\n=== {script} ===", flush=True)
            print(output, end="")
            if code:
                for pending in futures:
                    pending.cancel()
                raise SystemExit(code)
            total += assertion_count(output, script)

    missing = [script for script in BROWSER_SCRIPTS if script not in results]
    if missing:
        raise RuntimeError(f"Browser suites did not complete: {', '.join(missing)}")
    print(f"\nSENTINEL VALIDATION COMPLETE: {total} assertions passed.")
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
