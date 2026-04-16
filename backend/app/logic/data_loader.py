"""Curriculum data loading and cleaning."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from app.logic.config import settings


class DataLoadError(RuntimeError):
    """Raised when curriculum data cannot be loaded."""


def _sheet_csv_url(spreadsheet_id: str, gid: int) -> str:
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&gid={gid}"


def _read_csv(local_path: str | None, gid: int) -> pd.DataFrame:
    source = local_path or _sheet_csv_url(settings.spreadsheet_id, gid)
    try:
        return pd.read_csv(source)
    except Exception as exc:  # pragma: no cover - depends on external data source
        raise DataLoadError(f"Could not load curriculum data from {source}") from exc


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    for col in clean.columns:
        if clean[col].dtype == "object":
            clean[col] = clean[col].astype(str).str.strip()
    return clean


def _clean_topics(df: pd.DataFrame) -> pd.DataFrame:
    clean = _strip_strings(df)
    if "grade" in clean:
        clean["grade"] = clean["grade"].astype(str)
    if "topic_order" in clean:
        clean["topic_order"] = pd.to_numeric(clean["topic_order"], errors="coerce")
    if "is_core_topic" in clean:
        clean["is_core_topic"] = pd.to_numeric(clean["is_core_topic"], errors="coerce").fillna(0)
    return clean


def _clean_prereqs(df: pd.DataFrame) -> pd.DataFrame:
    clean = _strip_strings(df)
    for col in ["is_cross_grade", "is_cross_country"]:
        if col in clean:
            clean[col] = pd.to_numeric(clean[col], errors="coerce").fillna(0).astype(int)
    return clean


def _clean_cases(df: pd.DataFrame) -> pd.DataFrame:
    clean = _strip_strings(df)
    for col in ["overall_difficulty", "math_difficulty"]:
        if col in clean:
            clean[col] = pd.to_numeric(clean[col], errors="coerce")
    return clean


def _require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise DataLoadError(f"{label} data is missing required columns: {', '.join(missing)}")


@lru_cache(maxsize=1)
def load_curriculum_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    topics = _clean_topics(_read_csv(settings.topics_csv, settings.topics_gid))
    prereqs = _clean_prereqs(_read_csv(settings.prereq_csv, settings.prereq_gid))
    cases = _clean_cases(_read_csv(settings.student_cases_csv, settings.student_cases_gid))

    _require_columns(
        topics,
        {
            "topic_id",
            "country",
            "grade",
            "stream",
            "subject",
            "subject_branch",
            "topic_name_en",
            "topic_order",
            "is_core_topic",
        },
        "topics",
    )
    _require_columns(
        prereqs,
        {
            "from_topic_id",
            "to_topic_id",
            "relation_type",
            "strength",
            "is_cross_grade",
            "is_cross_country",
        },
        "prerequisite",
    )
    return topics, prereqs, cases

