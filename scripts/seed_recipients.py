"""Seed the recipients table from a CSV file."""

import csv
import sys
from pathlib import Path

# Allow running from project root without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal
from app.models import Recipient

DEFAULT_CSV = Path(__file__).parent / "recipients.sample.csv"


def seed(csv_path: Path) -> None:
    """Read a CSV of recipients and insert any that do not already exist.

    Expected columns: phone_number (required), name (optional).
    phone_number is normalised: whitespace stripped, leading + added if absent.
    Commits once after all rows are processed and prints a summary.
    """
    if not csv_path.exists():
        print(f"ERROR: file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    added = 0
    skipped = 0

    db = SessionLocal()
    try:
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw = row.get("phone_number", "").strip()
                if not raw:
                    continue
                phone = raw if raw.startswith("+") else f"+{raw}"
                name: str | None = row.get("name", "").strip() or None

                exists = (
                    db.query(Recipient)
                    .filter(Recipient.phone_number == phone)
                    .first()
                )
                if exists:
                    print(f"SKIP {phone} (already exists)")
                    skipped += 1
                else:
                    db.add(Recipient(phone_number=phone, name=name, whatsapp_reachable="unknown"))
                    print(f"ADD {phone}")
                    added += 1

        db.commit()
    finally:
        db.close()

    print(f"Done: {added} added, {skipped} skipped")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    seed(path)
