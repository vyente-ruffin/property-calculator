"""Portfolio persistence — SQLite storage for parsed/analyzed properties."""

import re
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

from src.core.logger import get_logger

log = get_logger("portfolio")

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "portfolio.db"

_TZ_PACIFIC = ZoneInfo("America/Los_Angeles")

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT,
    city TEXT,
    state TEXT,
    price INTEGER,
    total_units INTEGER,
    cap_rate TEXT,
    noi INTEGER,
    annual_rent INTEGER,
    monthly_rent INTEGER,
    unit_mix TEXT,
    date_on_market TEXT,
    property_url TEXT,
    description TEXT,
    parsed_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);
"""


def _now_pacific() -> str:
    """ISO 8601 timestamp in America/Los_Angeles (handles PST/PDT)."""
    return datetime.now(_TZ_PACIFIC).strftime("%Y-%m-%dT%H:%M:%S")


def _format_display_ts(iso_ts: str | None) -> str:
    """Convert ISO 8601 timestamp to MM/DD/YYYY hh:MM AM/PM for display."""
    if not iso_ts:
        return "--"
    try:
        dt = datetime.fromisoformat(iso_ts)
        return dt.strftime("%m/%d/%Y %I:%M %p")
    except (ValueError, TypeError):
        return iso_ts  # already in display format (legacy data)


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_TABLE)
    return conn


def _parse_int(val) -> int | None:
    if val is None:
        return None
    cleaned = str(val).replace("$", "").replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return int(Decimal(cleaned))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _normalize_address(addr: str) -> str:
    if not addr:
        return ""
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', addr.lower())).strip()


def save_property(data: dict) -> int:
    conn = _get_conn()
    try:
        address = data.get("Address") or data.get("address") or ""
        city = data.get("City") or data.get("city") or ""
        state = data.get("state", "")
        if not state and city:
            m = re.search(r',\s*([A-Z]{2})(?:\s|$)', city)
            if m:
                state = m.group(1)

        row = {
            "address": address,
            "city": city,
            "state": state or "CA",
            "price": _parse_int(data.get("Price") or data.get("price") or data.get("purchase_price")),
            "total_units": _parse_int(data.get("Total Units") or data.get("total_units")),
            "cap_rate": data.get("Cap Rate") or data.get("cap_rate"),
            "noi": _parse_int(data.get("NOI") or data.get("noi") or data.get("annual_noi_listing")),
            "annual_rent": _parse_int(
                data.get("Annual Rent Income (Actual)")
                or data.get("Annual Rent Income (Projected)")
                or data.get("annual_rent")
                or data.get("annual_gross_rents")
            ),
            "monthly_rent": _parse_int(
                data.get("Monthly Rental Income (Actual)")
                or data.get("Monthly Rental Income (Projected)")
                or data.get("monthly_rent")
            ),
            "unit_mix": data.get("Unit Mix Summary") or data.get("unit_mix"),
            "date_on_market": data.get("Date On Market") or data.get("date_on_market"),
            "property_url": data.get("Link") or data.get("property_url"),
            "description": data.get("Description") or data.get("description"),
        }

        # Deduplicate by normalized address
        norm = _normalize_address(address)
        if norm:
            existing = conn.execute("SELECT id, address FROM properties").fetchall()
            for ex in existing:
                if _normalize_address(ex["address"]) == norm:
                    pid = ex["id"]
                    sets = ", ".join(f"{k} = ?" for k in row.keys())
                    conn.execute(
                        f"UPDATE properties SET {sets}, parsed_at = ? WHERE id = ?",
                        list(row.values()) + [_now_pacific(), pid],
                    )
                    conn.commit()
                    log.info("property_updated id=%s address=%s price=%s", pid, address, row["price"])
                    return pid

        row["parsed_at"] = _now_pacific()
        cols = ", ".join(row.keys())
        placeholders = ", ".join(["?"] * len(row))
        cur = conn.execute(
            f"INSERT INTO properties ({cols}) VALUES ({placeholders})",
            list(row.values()),
        )
        conn.commit()
        pid = cur.lastrowid
        log.info("property_saved id=%s address=%s price=%s", pid, address, row["price"])
        return pid
    finally:
        conn.close()


def get_all_properties() -> list[dict]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM properties ORDER BY parsed_at DESC"
        ).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["parsed_at"] = _format_display_ts(d.get("parsed_at"))
            results.append(d)
        return results
    finally:
        conn.close()


def get_property(pid: int) -> dict | None:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM properties WHERE id = ?", (pid,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
