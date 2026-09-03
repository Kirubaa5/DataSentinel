import pandas as pd


def detect_duplicate_rows(df: pd.DataFrame) -> dict:
    """
    Detect completely duplicated rows in a dataset.
    """

    duplicate_mask = df.duplicated(keep=False)

    duplicate_count = int(duplicate_mask.sum())

    duplicate_percentage = (
        float((duplicate_count / len(df)) * 100)
        if len(df) > 0
        else 0.0
    )

    if duplicate_percentage >= 10:
        severity = "critical"
    elif duplicate_percentage >= 5:
        severity = "high"
    elif duplicate_percentage >= 1:
        severity = "medium"
    elif duplicate_percentage > 0:
        severity = "low"
    else:
        severity = "none"

    return {
        "check": "duplicate_rows",
        "duplicate_count": duplicate_count,
        "duplicate_percentage": round(duplicate_percentage, 2),
        "severity": severity,
    }