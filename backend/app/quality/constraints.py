import pandas as pd


def validate_numeric_constraints(
    df: pd.DataFrame,
    column: str,
    min_value: float | None = None,
    max_value: float | None = None,
    allow_zero: bool = True,
) -> dict:
    """
    Validate numeric values against configurable constraints.
    """

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    series = pd.to_numeric(df[column], errors="coerce").dropna()

    if series.empty:
        return {
            "check": "numeric_constraint",
            "column": column,
            "invalid_count": 0,
            "invalid_percentage": 0.0,
            "severity": "none",
        }

    invalid_mask = pd.Series(False, index=series.index)

    if min_value is not None:
        invalid_mask |= series < min_value

    if max_value is not None:
        invalid_mask |= series > max_value

    if not allow_zero:
        invalid_mask |= series == 0

    invalid_count = int(invalid_mask.sum())

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
        "check": "numeric_constraint",
        "column": column,
        "min_value": min_value,
        "max_value": max_value,
        "allow_zero": allow_zero,
        "invalid_count": invalid_count,
        "invalid_percentage": round(invalid_percentage, 2),
        "severity": severity,
    }