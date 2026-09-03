import pandas as pd

from app.core.config import QualityConfig
from app.quality.consistency import detect_category_inconsistency
from app.quality.constraints import validate_numeric_constraints
from app.quality.formats import validate_column_format
from app.quality.missing import detect_missing_values
from app.quality.duplicates import detect_duplicate_rows
from app.quality.types import validate_data_types
from app.quality.outliers import detect_iqr_outliers


def run_quality_checks(df: pd.DataFrame, config: QualityConfig | None = None) -> dict:
    """
    Run all currently implemented data-quality checks.
    """

    if df is None:
        raise ValueError("A dataframe is required")
    config = config or QualityConfig()
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

    results["numeric_constraints"] = []
    for column, options in config.numeric_constraints.items():
        results["numeric_constraints"].append(
            validate_numeric_constraints(df, column, **options)
        )

    results["format_validation"] = []
    for column, options in config.format_rules.items():
        results["format_validation"].append(
            validate_column_format(df, column, **options)
        )

    results["category_consistency"] = [
        detect_category_inconsistency(df, column)
        for column in config.consistency_columns
    ]

    return results