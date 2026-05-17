"""Run Lexora locally and capture a browser screenshot for the README."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_PATH = ROOT / "docs" / "assets" / "lexora-running-health.png"
LOCAL_DB_PATH = ROOT / "lexora_screenshot_run.db"
EDGE_CANDIDATES = [
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
]


def wait_for_server(url: str, timeout_seconds: int = 30) -> None:
    """Wait until the local server responds."""
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001 - diagnostic helper script
            last_error = exc
        time.sleep(0.5)

    raise RuntimeError(f"Server did not become ready: {last_error}")


def find_browser() -> Path:
    """Find an installed Chromium-based browser."""
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return candidate

    for executable in ("msedge", "chrome", "chromium"):
        found = shutil.which(executable)
        if found:
            return Path(found)

    raise RuntimeError("No Chromium-based browser found for screenshot capture")


def main() -> int:
    """Start the app, capture the docs screenshot, and shut the app down."""
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": f"sqlite+aiosqlite:///{LOCAL_DB_PATH.as_posix()}",
            "REDIS_URL": "redis://localhost:6379/0",
            "OPENAI_API_KEY": "sk-test-key",
            "SECRET_KEY": "test-secret-key-for-screenshot-run-32chars",
            "DOCUMENT_PROCESSING_MODE": "inline",
        }
    )

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8010",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        wait_for_server("http://127.0.0.1:8010/health")
        browser = find_browser()
        SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--disable-extensions",
                "--hide-scrollbars",
                "--window-size=1440,1100",
                f"--screenshot={SCREENSHOT_PATH}",
                "http://127.0.0.1:8010/health",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "Browser screenshot command failed:\n"
                f"stdout={result.stdout}\nstderr={result.stderr}"
            )

        print(f"Screenshot captured: {SCREENSHOT_PATH.relative_to(ROOT)}")
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)
        for _ in range(10):
            if not LOCAL_DB_PATH.exists():
                break
            try:
                LOCAL_DB_PATH.unlink()
                break
            except PermissionError:
                time.sleep(0.5)


if __name__ == "__main__":
    raise SystemExit(main())
