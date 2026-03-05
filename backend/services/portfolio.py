"""Portfolio persistence — SQLite storage for parsed/analyzed properties."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ai" / "logging"))
from logger import get_logger

log = get_logger("portfolio")

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "portfolio.db"

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
    purchase_price INTEGER,
    down_payment_pct INTEGER,
    interest_rate REAL,
    loan_years INTEGER,
    vacancy_rate REAL,
    other_expenses INTEGER,
    annual_cash_flow INTEGER,
    cash_on_cash REAL,
    verdict TEXT,
    parsed_at TEXT DEFAULT (strftime('%m/%d/%Y %I:%M %p', 'now', '-8 hours'))
);
"""


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_TABLE)
    return conn


def _parse_int(val) -> int | None:
    if val is None:
        return None
    s = str(val).replace("$", "").replace(",", "").replace(".00", "").strip()
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def save_property(data: dict) -> int:
    conn = _get_conn()
    try:
        row = {
            "address": data.get("Address") or data.get("address"),
            "city": data.get("City") or data.get("city"),
            "state": data.get("state", "CA"),
            "price": _parse_int(data.get("Price") or data.get("price")),
            "total_units": _parse_int(data.get("Total Units") or data.get("total_units")),
            "cap_rate": data.get("Cap Rate") or data.get("cap_rate"),
            "noi": _parse_int(data.get("NOI") or data.get("noi")),
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
            "purchase_price": _parse_int(data.get("purchase_price") or data.get("Price")),
            "down_payment_pct": _parse_int(data.get("down_payment_pct", 30)),
            "interest_rate": float(data.get("interest_rate", 6.5) or 6.5),
            "loan_years": _parse_int(data.get("loan_years", 25)),
            "vacancy_rate": float(data.get("vacancy_rate", 3) or 3),
            "other_expenses": _parse_int(data.get("other_expenses", 5000)),
            "annual_cash_flow": _parse_int(data.get("annual_cash_flow")),
            "cash_on_cash": float(data.get("cash_on_cash", 0) or 0),
            "verdict": data.get("verdict"),
        }

        # Deduplicate by address — update if exists, insert if new
        if row["address"]:
            existing = conn.execute(
                "SELECT id FROM properties WHERE address = ?", (row["address"],)
            ).fetchone()
            if existing:
                pid = existing["id"]
                sets = ", ".join(f"{k} = ?" for k in row.keys())
                conn.execute(
                    f"UPDATE properties SET {sets}, parsed_at = strftime('%m/%d/%Y %I:%M %p', 'now', '-8 hours') WHERE id = ?",
                    list(row.values()) + [pid],
                )
                conn.commit()
                log.info("property_updated", id=pid, address=row["address"], price=row["price"])
                return pid

        cols = ", ".join(row.keys())
        placeholders = ", ".join(["?"] * len(row))
        cur = conn.execute(
            f"INSERT INTO properties ({cols}) VALUES ({placeholders})",
            list(row.values()),
        )
        conn.commit()
        pid = cur.lastrowid
        log.info("property_saved", id=pid, address=row["address"], price=row["price"])
        return pid
    finally:
        conn.close()


def get_all_properties() -> list[dict]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM properties ORDER BY parsed_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
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
