import pandas as pd


def detect_category_inconsistency(
    df: pd.DataFrame,
    column: str,
) -> dict:
    """
    Detect category values that differ only because of
    capitalization or surrounding whitespace.
    """

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    series = df[column].dropna()

    if series.empty:
        return {
            "check": "category_consistency",
            "column": column,
            "inconsistent_groups": 0,
            "affected_values": 0,
            "severity": "none",
        }

    original_values = series.astype(str)

    normalized_values = (
        original_values
        .str.strip()
        .str.lower()
    )

    temp = pd.DataFrame(
        {
            "original": original_values,
            "normalized": normalized_values,
        }
    )

    groups = temp.groupby("normalized")["original"].nunique()

    inconsistent_groups = groups[groups > 1]

    affected_values = int(
        temp[
            temp["normalized"].isin(inconsistent_groups.index)
        ]["original"].nunique()
    )

    if inconsistent_groups.empty:
        severity = "none"
    elif len(inconsistent_groups) >= 10:
        severity = "high"
    elif len(inconsistent_groups) >= 5:
        severity = "medium"
    else:
        severity = "low"

    return {
        "check": "category_consistency",
        "column": column,
        "inconsistent_groups": int(len(inconsistent_groups)),
        "affected_values": affected_values,
        "severity": severity,
    }