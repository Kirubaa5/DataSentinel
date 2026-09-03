import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(
    df: pd.DataFrame,
    column: str,
    contamination: float = 0.01,
) -> dict:
    """
    Detect unusual numerical values using Isolation Forest.

    This identifies observations that behave differently
    from the majority of values.
    """

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")
    if not 0 < contamination <= 0.5:
        raise ValueError("contamination must be greater than 0 and at most 0.5")

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    valid_values = series.dropna()

    if len(valid_values) < 10:
        return {
            "check": "isolation_forest_anomaly",
            "column": column,
            "anomaly_count": 0,
            "anomaly_percentage": 0.0,
            "contamination": contamination,
            "affected_indexes": [],
            "anomaly_score_min": None,
            "anomaly_score_max": None,
            "severity": "none",
        }

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
    )

    predictions = model.fit_predict(
        valid_values.to_frame()
    )

    anomaly_count = int(
        (predictions == -1).sum()
    )
    anomaly_indexes = valid_values.index[predictions == -1].tolist()
    anomaly_scores = model.score_samples(valid_values.to_frame())

    anomaly_percentage = (
        anomaly_count / len(valid_values)
    ) * 100

    if anomaly_percentage >= 20:
        severity = "critical"
    elif anomaly_percentage >= 10:
        severity = "high"
    elif anomaly_percentage >= 5:
        severity = "medium"
    elif anomaly_count > 0:
        severity = "low"
    else:
        severity = "none"

    return {
        "check": "isolation_forest_anomaly",
        "column": column,
        "anomaly_count": anomaly_count,
        "anomaly_percentage": round(
            anomaly_percentage,
            2,
        ),
        "contamination": contamination,
        "affected_indexes": anomaly_indexes,
        "anomaly_score_min": float(anomaly_scores.min()),
        "anomaly_score_max": float(anomaly_scores.max()),
        "severity": severity,
    }