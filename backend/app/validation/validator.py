import pandas as pd


def validate_repair(
    original_df: pd.DataFrame,
    repaired_df: pd.DataFrame,
) -> dict:
    """
    Validate the result of a repair operation.
    """

    original_rows = len(original_df)
    repaired_rows = len(repaired_df)

    original_duplicates = int(
        original_df.duplicated().sum()
    )

    repaired_duplicates = int(
        repaired_df.duplicated().sum()
    )

    rows_removed = original_rows - repaired_rows

    duplicate_reduction = (
        original_duplicates - repaired_duplicates
    )

    validation_passed = (
        repaired_rows <= original_rows
        and repaired_duplicates <= original_duplicates
    )

    return {
        "validation_passed": validation_passed,
        "original_rows": original_rows,
        "repaired_rows": repaired_rows,
        "rows_removed": rows_removed,
        "original_duplicates": original_duplicates,
        "repaired_duplicates": repaired_duplicates,
        "duplicate_reduction": duplicate_reduction,
    }