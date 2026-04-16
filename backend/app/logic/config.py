"""Runtime configuration for curriculum data sources."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DataSettings:
    spreadsheet_id: str = os.getenv(
        "GAP_SPREADSHEET_ID",
        "1_4zwnY568JzDVN0yXJXWcBA0fp0C-8HtlMRlC6SgP5o",
    )
    topics_gid: int = int(os.getenv("GAP_TOPICS_GID", "0"))
    prereq_gid: int = int(os.getenv("GAP_PREREQ_GID", "2139026213"))
    student_cases_gid: int = int(os.getenv("GAP_STUDENT_CASES_GID", "1931131840"))
    topics_csv: str | None = os.getenv("GAP_TOPICS_CSV")
    prereq_csv: str | None = os.getenv("GAP_PREREQ_CSV")
    student_cases_csv: str | None = os.getenv("GAP_STUDENT_CASES_CSV")


settings = DataSettings()

