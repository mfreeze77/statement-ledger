"""Optional real Chromium smoke test; requires playwright and installed Chromium.
Uses a temporary synthetic DB and a throwaway token. No live source/provider calls.
"""

import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from statement_ledger.acceleration_demo import (  # noqa: E402
    seed_acceleration,  # noqa: E402 - direct-script source bootstrap
)
from statement_ledger.service import Ledger  # noqa: E402 - direct-script source bootstrap
from statement_ledger.store import Store  # noqa: E402 - direct-script source bootstrap


def main():
    from playwright.sync_api import expect, sync_playwright

    out = ROOT / "validation"
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / "ui.sqlite3"
        s = Store(db, initialize=True)
        seed_acceleration(Ledger(s))
        s.close()
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        token = secrets.token_urlsafe(40)
        env = {
            **os.environ,
            "PYTHONPATH": str(ROOT / "src"),
            "SL_API_TOKEN": token,
            "SL_ENABLE_JEV": "0",
        }
        log = (Path(temp) / "server.log").open("w")
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "statement_ledger.cli",
                "--db",
                str(db),
                "serve",
                "--port",
                str(port),
            ],
            env=env,
            stdout=log,
            stderr=log,
        )
        try:
            import httpx

            for _ in range(50):
                try:
                    if httpx.get(f"http://127.0.0.1:{port}/healthz").status_code == 200:
                        break
                except httpx.HTTPError:
                    time.sleep(0.1)
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    executable_path=shutil.which("chromium") or None,
                    args=["--no-sandbox"],
                )
                page = browser.new_page(viewport={"width": 1440, "height": 1050})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
                page.locator("#token").fill(token)
                page.locator("#connect").click()
                expect(page.locator("#content")).to_contain_text("Dana Example")
                page.locator("[data-view=profiles]").click()
                expect(page.locator("#content h2")).to_have_text("Learned phrase profiles")
                expect(page.locator("table").first).to_be_visible()
                page.screenshot(path=str(out / "ui-phrase-profiles.png"), full_page=True)
                page.locator("[data-view=localization]").click()
                expect(page.locator("[aria-label=Transcript]")).to_be_visible()
                page.locator("[aria-label=Transcript]").select_option("style-heldout-transcript")
                page.locator('[aria-label="Processing mode"]').select_option("assist")
                page.get_by_role("button", name="Build local plan — no Jev call").click()
                expect(page.locator(".window-result")).to_contain_text(
                    "Identity remains unconfirmed"
                )
                page.screenshot(path=str(out / "ui-speaker-windows.png"), full_page=True)
                page.locator("[data-view=claims]").click()
                page.locator('[aria-label="Claim search"]').fill("Synthetic Lab samples")
                page.get_by_role("button", name="Search local claim index").click()
                expect(page.locator("#content .card").first).to_contain_text("Synthetic Lab")
                page.screenshot(path=str(out / "ui-claim-library.png"), full_page=True)
                assert not errors, errors
                browser.close()
            result = {
                "executed": True,
                "browser": "Chromium via Playwright",
                "data": "synthetic",
                "views": ["people", "phrase_profiles", "speaker_windows", "claim_library"],
                "page_errors": errors,
                "provider_calls": 0,
            }
            (out / "ui-smoke.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result))
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
            log.close()


if __name__ == "__main__":
    main()
