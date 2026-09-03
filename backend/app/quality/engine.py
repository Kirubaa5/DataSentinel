import pandas as pd

from app.quality.missing import detect_missing_values
from app.quality.duplicates import detect_duplicate_rows
from app.quality.types import validate_data_types
from app.quality.outliers import detect_iqr_outliers


def run_quality_checks(df: pd.DataFrame) -> dict:
    """
    Run all currently implemented data-quality checks.
    """

    results = {}

    # Missing values
    results["missing_values"] = detect_missing_values(df)

    # Duplicate rows
    results["duplicate_rows"] = detect_duplicate_rows(df)

    # Data type validation
    results["data_type_validation"] = validate_data_types(df)

    # Outlier detection
    results["outliers"] = []

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:
        results["outliers"].append(
            detect_iqr_outliers(df, column)
        )

    return results