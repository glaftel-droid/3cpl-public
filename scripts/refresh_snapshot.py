#!/usr/bin/env python3
"""Refresh a public, contacts-free static snapshot from CT103 read APIs."""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = os.environ.get("PLANT_API_BASE", "http://yuharui.duckdns.org:888").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data.json"
TIMEOUT = 20


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "3cpl-github-snapshot/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=TIMEOUT) as response:
        if response.status != 200:
            raise RuntimeError(f"{url} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def iso_date(value: object, *, optional: bool = False) -> str:
    text = str(value or "")
    if optional and not text:
        return ""
    date.fromisoformat(text)
    return text


def main() -> int:
    repair_payload = fetch_json(BASE + "/api/repair.php")
    cpl_payload = fetch_json(BASE + "/api/cpl.php?action=list")
    if repair_payload.get("success") is not True or not isinstance(repair_payload.get("data"), list):
        raise RuntimeError("repair API returned an unexpected shape")
    if cpl_payload.get("ok") is not True or not isinstance(cpl_payload.get("overrides"), dict):
        raise RuntimeError("3CPL API returned an unexpected shape")

    # Deliberately whitelist only operational schedule fields; never export contacts.
    repairs = []
    for row in repair_payload["data"]:
        if not isinstance(row, dict):
            continue
        start = iso_date(row.get("start_date"))
        end = iso_date(row.get("end_date"), optional=True) or start
        if end < start:
            raise RuntimeError(f"invalid repair date range: {start} -> {end}")
        repairs.append({
            "facility": str(row.get("facility") or "")[:40],
            "repair_type": str(row.get("repair_type") or "")[:40],
            "start_date": start,
            "end_date": end,
            "content": str(row.get("content") or "")[:160],
            "status": str(row.get("status") or "pending")[:24],
        })
    repairs.sort(key=lambda r: (r["start_date"], r["facility"], r["repair_type"]))

    overrides = {}
    for key, value in cpl_payload["overrides"].items():
        day = str(key)
        iso_date(day)
        state = str(value)
        if state not in ("출", "휴"):
            raise RuntimeError(f"invalid 3CPL override for {day}")
        overrides[day] = state

    snapshot = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repairs": repairs,
        "cpl_overrides": overrides,
    }
    encoded = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=".data.", suffix=".json", dir=ROOT)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, TARGET)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
    print(f"Updated {TARGET.name}: {len(repairs)} repair records, {len(overrides)} 3CPL overrides; contacts omitted.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Snapshot refresh failed; kept the previous data.json: {exc}", file=sys.stderr)
        raise SystemExit(1)
