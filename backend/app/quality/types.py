import pandas as pd


def validate_data_types(df: pd.DataFrame) -> list[dict]:
    """
    Detect columns containing mixed Python data types.

    The dominant Python type is treated as the expected type.
    Values belonging to other types are reported as unexpected.
    """

    findings = []

    for column in df.columns:
        series = df[column].dropna()

        if series.empty:
            continue

        type_counts = series.map(
            lambda value: type(value).__name__
        ).value_counts()

        if len(type_counts) <= 1:
            continue

        dominant_type = type_counts.index[0]
        unexpected_types = type_counts.index[1:]

        unexpected_count = int(type_counts.iloc[1:].sum())
        total_values = len(series)

        unexpected_percentage = (
            unexpected_count / total_values
        ) * 100

        if unexpected_percentage >= 10:
            severity = "high"
        elif unexpected_percentage >= 1:
            severity = "medium"
        else:
            severity = "low"

        findings.append(
            {
                "check": "data_type_validation",
                "column": column,
                "dominant_type": dominant_type,
                "unexpected_types": list(unexpected_types),
                "unexpected_count": unexpected_count,
                "unexpected_percentage": round(
                    unexpected_percentage, 4
                ),
                "severity": severity,
            }
        )

    return findings