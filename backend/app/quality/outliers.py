import pandas as pd


def detect_iqr_outliers(
    df: pd.DataFrame,
    column: str,
) -> dict:
    """
    Detect numerical outliers using the IQR method.
    """

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    series = pd.to_numeric(df[column], errors="coerce").dropna()

    if series.empty:
        return {
            "check": "iqr_outlier",
            "column": column,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "lower_bound": None,
            "upper_bound": None,
            "severity": "none",
        }

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outlier_mask = (
        (series < lower_bound)
        | (series > upper_bound)
    )

    outlier_count = int(outlier_mask.sum())

    outlier_percentage = (
        outlier_count / len(series)
    ) * 100

    if outlier_percentage >= 20:
        severity = "critical"
    elif outlier_percentage >= 10:
        severity = "high"
    elif outlier_percentage >= 5:
        severity = "medium"
    elif outlier_percentage > 0:
        severity = "low"
    else:
        severity = "none"

    return {
        "check": "iqr_outlier",
        "column": column,
        "q1": round(float(q1), 4),
        "q3": round(float(q3), 4),
        "iqr": round(float(iqr), 4),
        "lower_bound": round(float(lower_bound), 4),
        "upper_bound": round(float(upper_bound), 4),
        "outlier_count": outlier_count,
        "outlier_percentage": round(outlier_percentage, 2),
        "severity": severity,
    }