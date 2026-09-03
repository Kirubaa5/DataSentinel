import re

import pandas as pd


def validate_column_format(
    df: pd.DataFrame,
    column: str,
    pattern: str,
    format_name: str,
) -> dict:
    """
    Validate non-null values in a column against a regex pattern.
    """

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    series = df[column].dropna().astype(str)

    if series.empty:
        return {
            "check": "format_validation",
            "column": column,
            "format": format_name,
            "total_values": 0,
            "invalid_count": 0,
            "invalid_percentage": 0.0,
            "severity": "none",
        }

    try:
        valid_mask = series.apply(
            lambda value: bool(re.fullmatch(pattern, value))
        )
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern for {column}: {pattern}") from exc

    invalid_count = int((~valid_mask).sum())

    invalid_percentage = (
        invalid_count / len(series)
    ) * 100

    if invalid_percentage >= 20:
        severity = "critical"
    elif invalid_percentage >= 10:
        severity = "high"
    elif invalid_percentage >= 5:
        severity = "medium"
    elif invalid_percentage > 0:
        severity = "low"
    else:
        severity = "none"

    return {
        "check": "format_validation",
        "column": column,
        "format": format_name,
        "total_values": len(series),
        "invalid_count": invalid_count,
        "invalid_percentage": round(invalid_percentage, 2),
        "severity": severity,
    }