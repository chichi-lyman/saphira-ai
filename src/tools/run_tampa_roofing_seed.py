"""Run the seeded Tampa Bay roofing prospects through Saphira's review pipeline.

This command reads only the checked-in seed CSV. It does not discover leads and
never sends outbound messages. Website analysis is public-page inspection only.
"""
from __future__ import annotations

import csv
from pathlib import Path

from src.tools.free_scraper import Lead, normalize_leads
from src.tools.tampa_roofing_pipeline import profile_lead, write_approval_queue, write_summary

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "storage" / "seeds" / "tampa_bay_roofing_seed.csv"
OUTPUT_DIR = ROOT / "storage"
QUEUE = OUTPUT_DIR / "tampa_roofing_approval_queue.csv"
SUMMARY = OUTPUT_DIR / "tampa_roofing_approval_summary.md"


def load_seed(path: Path = SEED) -> list[Lead]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return normalize_leads(
            Lead(
                business_name=row.get("company_name", ""),
                website=row.get("website", ""),
                city=row.get("city", ""),
                state=row.get("state", ""),
                industry="Roofing Contractors",
                source_url=row.get("source_url", ""),
                source_name=row.get("source_name", ""),
                discovered_at=row.get("discovered_at", ""),
            )
            for row in reader
        )


def run() -> tuple[Path, Path]:
    leads = load_seed()
    profiles = [profile_lead(lead) for lead in leads[:50]]
    queue = write_approval_queue(profiles, QUEUE)
    summary = write_summary(profiles, SUMMARY)
    return queue, summary


if __name__ == "__main__":
    queue, summary = run()
    print(f"Generated approval queue: {queue}")
    print(f"Generated review summary: {summary}")
    print(f"Profiles: {len(load_seed())}")
    print("Outbound messaging: DISABLED; approval_status defaults to PENDING_REVIEW")
