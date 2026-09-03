import pandas as pd


def repair_duplicate_rows(
    df: pd.DataFrame,
    approved: bool = False,
) -> tuple[pd.DataFrame, dict]:
    """
    Remove completely duplicated rows only when explicitly approved.
    """

    duplicate_count = int(df.duplicated().sum())

    if not approved:
        return df.copy(), {
            "repair": "duplicate_rows",
            "approved": False,
            "changed": False,
            "removed_count": 0,
            "message": (
                "Duplicate removal was not approved. "
                "Original dataset remains unchanged."
            ),
        }

    cleaned_df = df.drop_duplicates().reset_index(drop=True)

    removed_count = len(df) - len(cleaned_df)

    return cleaned_df, {
        "repair": "duplicate_rows",
        "approved": True,
        "changed": removed_count > 0,
        "removed_count": removed_count,
        "message": (
            f"Removed {removed_count} completely duplicated rows."
        ),
    }