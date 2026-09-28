"""CPU Compose readiness/auth smoke test, no external credentials or calls."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

for attempt in range(60):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/readyz", timeout=2) as response:
            if response.status == 200:
                break
    except (OSError, urllib.error.URLError):
        time.sleep(1)
else:
    raise SystemExit("Container API did not become ready")
values = {}
for line in Path(".env").read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        values[key] = value.strip().strip("\"'")
token = values.get("SL_SECRET_API_TOKEN") or values.get("SL_API_TOKEN")
request = urllib.request.Request(
    "http://127.0.0.1:8765/api/jobs", headers={"Authorization": "Bearer " + str(token)}
)
with urllib.request.urlopen(request, timeout=5) as response:
    json.load(response)
try:
    urllib.request.urlopen("http://127.0.0.1:8765/api/jobs", timeout=5)
except urllib.error.HTTPError as exc:
    if exc.code != 401:
        raise
else:
    raise SystemExit("Unauthenticated jobs endpoint accepted a request")
print("Container readiness and authenticated operator boundary passed")
