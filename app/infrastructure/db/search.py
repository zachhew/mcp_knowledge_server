from __future__ import annotations

from sqlalchemy import func


def build_websearch_tsquery(query: str):
    return func.websearch_to_tsquery("english", query)


def build_search_vector(title_col, summary_col, content_col, tags_col):
    return func.to_tsvector(
        "english",
        func.coalesce(title_col, "")
        + " "
        + func.coalesce(summary_col, "")
        + " "
        + func.coalesce(content_col, "")
        + " "
        + func.coalesce(tags_col, ""),
    )