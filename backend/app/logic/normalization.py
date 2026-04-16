"""Normalization helpers lifted from the original prototype."""

from __future__ import annotations

import pandas as pd


GRADE_MAP_AR_TO_CANONICAL = {
    "Ø§Ù„ØªØ§Ø³Ø¹": "9",
    "Ø§Ù„Ø¹Ø§Ø´Ø±": "10",
    "Ø§Ù„Ø­Ø§Ø¯ÙŠ Ø¹Ø´Ø±": "11",
    "Ø¨ÙƒØ§Ù„ÙˆØ±ÙŠØ§": "12",
    "Ø§Ù„Ø«Ø§Ù…Ù†": "8",
    "Ø§Ù„Ø³Ø§Ø¨Ø¹": "7",
    "Ø§Ù„Ø³Ø§Ø¯Ø³": "6",
    "Ø§Ù„Ø®Ø§Ù…Ø³": "5",
}

STREAM_MAP_AR_TO_CANONICAL = {
    "Ø¹Ù„Ù…ÙŠ": "Scientific",
    "Ø§Ø¯Ø¨ÙŠ": "Literary",
    "Ø£Ø¯Ø¨ÙŠ": "Literary",
    "Ø¹Ø§Ù…": "General",
    "Ø¬Ù†Ø±Ø§Ù„": "General",
    "General": "General",
    "Scientific": "Scientific",
    "Literary": "Literary",
}

COUNTRY_MAP_AR_TO_CANONICAL = {
    "Ø³ÙˆØ±ÙŠØ§": "Syria",
    "ØªØ±ÙƒÙŠØ§": "Turkey",
    "Syria": "Syria",
    "Turkey": "Turkey",
}


def normalize_grade(grade_value: str | int | None) -> str:
    grade_value = "" if grade_value is None else str(grade_value).strip()
    return GRADE_MAP_AR_TO_CANONICAL.get(grade_value, grade_value)


def normalize_stream(stream_value: str | None) -> str:
    stream_value = "" if stream_value is None else str(stream_value).strip()
    return STREAM_MAP_AR_TO_CANONICAL.get(stream_value, stream_value)


def normalize_country(country_value: str | None) -> str:
    country_value = "" if country_value is None else str(country_value).strip()
    return COUNTRY_MAP_AR_TO_CANONICAL.get(country_value, country_value)


def parse_grade_list(grades: list[str] | str | None) -> set[str]:
    if grades is None or (isinstance(grades, float) and pd.isna(grades)):
        return set()

    if isinstance(grades, list):
        parts = grades
    else:
        parts = str(grades).split(",")

    return {normalize_grade(part) for part in parts if str(part).strip()}

