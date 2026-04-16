"""Backend-friendly curriculum gap analysis service."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.logic.data_loader import load_curriculum_data
from app.logic.normalization import (
    normalize_country,
    normalize_grade,
    normalize_stream,
    parse_grade_list,
)
from app.models.student_case import CurriculumGraphInput, StudentCaseInput


STATUS_LABEL_MAP = {
    "likely_missed_due_to_switch": "Needs support before or alongside target topic",
    "likely_covered_abroad": "Likely already covered abroad",
    "bridge_available_outside_student_path": "Possible bridge exists, but outside the student's studied path",
    "currently_in_target_grade_path": "Part of the current target-grade learning path",
}


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    clean = df.where(pd.notna(df), None)
    return clean.to_dict(orient="records")


def get_target_topics(
    topics_df: pd.DataFrame,
    target_country: str,
    target_grade: str,
    target_stream: str | None,
    subject_focus: str,
    core_only: bool = True,
) -> pd.DataFrame:
    df = topics_df[
        (topics_df["country"] == target_country)
        & (topics_df["grade"] == str(target_grade))
        & (topics_df["subject"] == subject_focus)
    ].copy()

    if target_stream:
        df = df[df["stream"] == target_stream]

    if core_only:
        df = df[df["is_core_topic"] == 1]

    return df.sort_values(["subject_branch", "topic_order"]).reset_index(drop=True)


def build_direct_prereq_links_for_targets(
    topics_df: pd.DataFrame,
    prereq_df: pd.DataFrame,
    target_topics: pd.DataFrame,
) -> pd.DataFrame:
    target_ids = set(target_topics["topic_id"].tolist())
    edges = prereq_df[prereq_df["to_topic_id"].isin(target_ids)].copy()
    if edges.empty:
        return pd.DataFrame()

    target_info = topics_df[["topic_id", "topic_name_en", "grade", "stream", "subject_branch"]].rename(
        columns={
            "topic_id": "to_topic_id",
            "topic_name_en": "target_topic_name_en",
            "grade": "target_grade",
            "stream": "target_stream",
            "subject_branch": "target_subject_branch",
        }
    )
    prereq_info = topics_df[
        ["topic_id", "topic_name_en", "grade", "stream", "subject_branch", "country"]
    ].rename(
        columns={
            "topic_id": "from_topic_id",
            "topic_name_en": "prereq_topic_name_en",
            "grade": "prereq_grade",
            "stream": "prereq_stream",
            "subject_branch": "prereq_subject_branch",
            "country": "prereq_country",
        }
    )

    enriched = edges.merge(target_info, on="to_topic_id", how="left")
    enriched = enriched.merge(prereq_info, on="from_topic_id", how="left")
    return enriched.sort_values(["to_topic_id", "from_topic_id"]).reset_index(drop=True)


def build_candidate_support_topics(direct_links: pd.DataFrame) -> pd.DataFrame:
    if direct_links.empty:
        return pd.DataFrame()

    grouped = (
        direct_links.groupby(
            [
                "from_topic_id",
                "prereq_topic_name_en",
                "prereq_country",
                "prereq_grade",
                "prereq_stream",
                "prereq_subject_branch",
            ],
            dropna=False,
        )
        .agg(
            support_count=("to_topic_id", "nunique"),
            relation_types=("relation_type", lambda x: ", ".join(sorted(set(map(str, x))))),
            strengths=("strength", lambda x: ", ".join(sorted(set(map(str, x))))),
            cross_grade_edges=("is_cross_grade", "sum"),
            cross_country_edges=("is_cross_country", "sum"),
            supported_targets=("target_topic_name_en", lambda x: " | ".join(sorted(set(map(str, x))))),
        )
        .reset_index()
    )

    return grouped.sort_values(
        ["support_count", "cross_grade_edges", "cross_country_edges", "from_topic_id"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def infer_prereq_coverage_status(
    row: pd.Series,
    origin_country_norm: str,
    studied_abroad_grades: set[str],
    normalized_target_grade: str,
) -> str:
    prereq_country = str(row.get("prereq_country", "")).strip()
    prereq_grade = str(row.get("prereq_grade", "")).strip()
    cross_country_edges = row.get("cross_country_edges", 0) or 0

    if prereq_country == origin_country_norm and prereq_grade in studied_abroad_grades:
        return "likely_covered_abroad"
    if prereq_country == "Syria" and prereq_grade in studied_abroad_grades:
        return "likely_missed_due_to_switch"
    if prereq_country == origin_country_norm and prereq_grade not in studied_abroad_grades and cross_country_edges > 0:
        return "bridge_available_outside_student_path"
    if prereq_country == "Syria" and prereq_grade == normalized_target_grade:
        return "currently_in_target_grade_path"
    return "currently_in_target_grade_path"


def add_coverage_status(
    candidate_support_topics: pd.DataFrame,
    case_input: StudentCaseInput,
    normalized_target_grade: str,
) -> pd.DataFrame:
    if candidate_support_topics.empty:
        return candidate_support_topics

    origin_country_norm = normalize_country(case_input.origin_country)
    studied_abroad_grades = parse_grade_list(case_input.grades_studied_abroad)
    result = candidate_support_topics.copy()
    result["coverage_status"] = result.apply(
        infer_prereq_coverage_status,
        axis=1,
        origin_country_norm=origin_country_norm,
        studied_abroad_grades=studied_abroad_grades,
        normalized_target_grade=normalized_target_grade,
    )
    result["status_label"] = result["coverage_status"].map(STATUS_LABEL_MAP)
    return result


def build_target_prereq_report(
    direct_links: pd.DataFrame,
    candidate_support_topics: pd.DataFrame,
) -> pd.DataFrame:
    if direct_links.empty:
        return pd.DataFrame()

    support_lookup = candidate_support_topics[
        [
            "from_topic_id",
            "coverage_status",
            "status_label",
            "prereq_country",
            "support_count",
            "cross_grade_edges",
            "cross_country_edges",
            "relation_types",
            "strengths",
        ]
    ].drop_duplicates(subset=["from_topic_id"])

    report = direct_links.merge(support_lookup, on="from_topic_id", how="left", suffixes=("", "_agg"))
    columns = [
        "to_topic_id",
        "target_topic_name_en",
        "from_topic_id",
        "prereq_topic_name_en",
        "prereq_country",
        "prereq_grade",
        "prereq_stream",
        "prereq_subject_branch",
        "relation_type",
        "strength",
        "is_cross_grade",
        "is_cross_country",
        "coverage_status",
        "status_label",
        "support_count",
    ]
    return report[columns].sort_values(["to_topic_id", "coverage_status", "from_topic_id"]).reset_index(drop=True)


def build_student_graph_nodes(target_topics: pd.DataFrame, candidate_support_topics: pd.DataFrame) -> pd.DataFrame:
    target_nodes = target_topics[["topic_id", "topic_name_en", "subject_branch"]].rename(
        columns={"topic_id": "id", "topic_name_en": "label", "subject_branch": "group"}
    )
    target_nodes["type"] = "target_topic"
    target_nodes["status"] = "target"

    if candidate_support_topics.empty:
        return target_nodes.drop_duplicates("id").reset_index(drop=True)

    prereq_nodes = candidate_support_topics[
        ["from_topic_id", "prereq_topic_name_en", "prereq_subject_branch", "coverage_status"]
    ].rename(
        columns={
            "from_topic_id": "id",
            "prereq_topic_name_en": "label",
            "prereq_subject_branch": "group",
            "coverage_status": "status",
        }
    )
    prereq_nodes["type"] = "prereq_topic"

    return pd.concat([target_nodes, prereq_nodes], ignore_index=True).drop_duplicates("id").reset_index(drop=True)


def build_student_graph_edges(target_prereq_report: pd.DataFrame) -> pd.DataFrame:
    if target_prereq_report.empty:
        return pd.DataFrame(columns=["source", "target", "type", "strength", "status"])

    return target_prereq_report[
        ["from_topic_id", "to_topic_id", "relation_type", "strength", "coverage_status"]
    ].rename(
        columns={
            "from_topic_id": "source",
            "to_topic_id": "target",
            "relation_type": "type",
            "coverage_status": "status",
        }
    ).reset_index(drop=True)


def analyze_student_case(case_input: StudentCaseInput) -> dict[str, Any]:
    topics_df, prereq_df, _cases_df = load_curriculum_data()

    normalized_target_country = normalize_country(case_input.target_country)
    normalized_target_grade = normalize_grade(case_input.target_grade)
    normalized_target_stream = normalize_stream(case_input.target_stream)
    normalized_subject_focus = case_input.subject_focus.strip() or "Math"

    target_topics = get_target_topics(
        topics_df,
        normalized_target_country,
        normalized_target_grade,
        normalized_target_stream,
        normalized_subject_focus,
        core_only=True,
    )
    direct_links = build_direct_prereq_links_for_targets(topics_df, prereq_df, target_topics)
    support_topics = build_candidate_support_topics(direct_links)
    support_topics = add_coverage_status(support_topics, case_input, normalized_target_grade)
    target_report = build_target_prereq_report(direct_links, support_topics)

    teacher_alert = target_report[target_report["coverage_status"] == "likely_missed_due_to_switch"].copy()
    teacher_alert = teacher_alert[
        [
            "target_topic_name_en",
            "prereq_topic_name_en",
            "relation_type",
            "strength",
            "prereq_grade",
            "prereq_country",
            "status_label",
        ]
    ] if not teacher_alert.empty else teacher_alert

    support_first = support_topics[support_topics["coverage_status"] == "likely_missed_due_to_switch"].copy()
    if not support_first.empty:
        support_first = support_first.sort_values(
            ["support_count", "cross_grade_edges", "from_topic_id"],
            ascending=[False, False, True],
        )[
            [
                "from_topic_id",
                "prereq_topic_name_en",
                "prereq_grade",
                "prereq_stream",
                "support_count",
                "relation_types",
                "strengths",
                "coverage_status",
                "status_label",
                "supported_targets",
            ]
        ]

    student_nodes = build_student_graph_nodes(target_topics, support_topics)
    student_edges = build_student_graph_edges(target_report)
    studied_abroad_grades = sorted(parse_grade_list(case_input.grades_studied_abroad))

    summary = {
        "case_id": case_input.case_id,
        "origin_country": normalize_country(case_input.origin_country),
        "grades_studied_abroad": studied_abroad_grades,
        "last_completed_grade_abroad": normalize_grade(case_input.last_completed_grade_abroad),
        "target_country": normalized_target_country,
        "target_grade": normalized_target_grade,
        "target_stream": normalized_target_stream,
        "subject_focus": normalized_subject_focus,
        "overall_difficulty": case_input.overall_difficulty,
        "math_difficulty": case_input.math_difficulty,
        "n_target_topics": len(target_topics),
        "n_direct_prereq_links": len(direct_links),
        "n_support_topics": len(support_topics),
        "n_likely_missed_topics": int((support_topics.get("coverage_status") == "likely_missed_due_to_switch").sum())
        if not support_topics.empty
        else 0,
        "n_likely_covered_abroad_topics": int((support_topics.get("coverage_status") == "likely_covered_abroad").sum())
        if not support_topics.empty
        else 0,
        "n_bridge_topics_outside_path": int(
            (support_topics.get("coverage_status") == "bridge_available_outside_student_path").sum()
        )
        if not support_topics.empty
        else 0,
        "n_current_target_grade_support_topics": int(
            (support_topics.get("coverage_status") == "currently_in_target_grade_path").sum()
        )
        if not support_topics.empty
        else 0,
    }

    return {
        "summary": summary,
        "teacher_alert_report": _records(teacher_alert),
        "support_first_topics": _records(support_first),
        "graph_summary": {
            "nodes_count": len(student_nodes),
            "edges_count": len(student_edges),
            "preview_nodes": _records(student_nodes.head(12)),
            "preview_edges": _records(student_edges.head(12)),
        },
    }


def build_student_graph(case_input: StudentCaseInput) -> dict[str, Any]:
    topics_df, prereq_df, _cases_df = load_curriculum_data()
    target_country = normalize_country(case_input.target_country)
    target_grade = normalize_grade(case_input.target_grade)
    target_stream = normalize_stream(case_input.target_stream)
    subject_focus = case_input.subject_focus.strip() or "Math"

    target_topics = get_target_topics(topics_df, target_country, target_grade, target_stream, subject_focus)
    direct_links = build_direct_prereq_links_for_targets(topics_df, prereq_df, target_topics)
    support_topics = build_candidate_support_topics(direct_links)
    support_topics = add_coverage_status(support_topics, case_input, target_grade)
    target_report = build_target_prereq_report(direct_links, support_topics)

    return {
        "nodes": _records(build_student_graph_nodes(target_topics, support_topics)),
        "edges": _records(build_student_graph_edges(target_report)),
    }


def build_curriculum_graph(input_data: CurriculumGraphInput) -> dict[str, Any]:
    topics_df, prereq_df, _cases_df = load_curriculum_data()
    country = normalize_country(input_data.country)
    grade = normalize_grade(input_data.grade)
    stream = normalize_stream(input_data.stream)

    slice_topics = topics_df[
        (topics_df["country"] == country)
        & (topics_df["grade"] == str(grade))
        & (topics_df["subject"] == input_data.subject)
    ].copy()
    if stream:
        slice_topics = slice_topics[slice_topics["stream"] == stream]
    if input_data.core_only:
        slice_topics = slice_topics[slice_topics["is_core_topic"] == 1]

    topic_ids = set(slice_topics["topic_id"].tolist())
    slice_edges = prereq_df[
        prereq_df["from_topic_id"].isin(topic_ids) & prereq_df["to_topic_id"].isin(topic_ids)
    ].copy()

    nodes = slice_topics[["topic_id", "topic_name_en", "subject_branch"]].rename(
        columns={"topic_id": "id", "topic_name_en": "label", "subject_branch": "group"}
    )
    nodes["type"] = "curriculum_topic"
    nodes["status"] = "curriculum"

    edges = slice_edges[["from_topic_id", "to_topic_id", "relation_type", "strength"]].rename(
        columns={"from_topic_id": "source", "to_topic_id": "target", "relation_type": "type"}
    )

    return {"nodes": _records(nodes), "edges": _records(edges)}

