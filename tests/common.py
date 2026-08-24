"""Shared helpers for the SENTINEL browser regression suite."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(__file__).resolve().parent / "assets"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
URL = os.environ.get("SENTINEL_URL", "http://127.0.0.1:8767/index.html")


def chromium_path() -> str | None:
    explicit = os.environ.get("SENTINEL_CHROMIUM")
    if explicit:
        return explicit
    # Prefer Playwright's bundled Chromium so host enterprise URL policies do not
    # invalidate local-origin acceptance tests. Set SENTINEL_USE_SYSTEM_CHROMIUM=1
    # to exercise an explicitly managed system browser.
    if os.environ.get("SENTINEL_USE_SYSTEM_CHROMIUM") == "1":
        return shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    bundled = sorted((Path.home() / ".cache" / "ms-playwright").glob("chromium-*/chrome-linux64/chrome"), reverse=True)
    if bundled:
        return str(bundled[0])
    return shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")


def launch_browser(playwright, extra_args: list[str] | None = None):
    """Launch Chromium, preferring a system browser when one is available."""
    kwargs = {"headless": True, "args": ["--no-sandbox", *(extra_args or [])]}
    executable = chromium_path()
    if executable:
        kwargs["executable_path"] = executable
    return playwright.chromium.launch(**kwargs)
