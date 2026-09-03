import pandas as pd


def detect_missing_values(df: pd.DataFrame) -> list[dict]:
    """
    Detect missing values in each column.
    """

    findings = []

    for column in df.columns:
        missing_count = int(df[column].isna().sum())

        if missing_count == 0:
            continue

        missing_percentage = float(
            (missing_count / len(df)) * 100
        )

        if missing_percentage >= 20:
            severity = "critical"
        elif missing_percentage >= 10:
            severity = "high"
        elif missing_percentage >= 5:
            severity = "medium"
        else:
            severity = "low"

        findings.append(
            {
                "check": "missing_values",
                "column": column,
                "missing_count": missing_count,
                "missing_percentage": round(missing_percentage, 2),
                "severity": severity,
            }
        )

    return findings