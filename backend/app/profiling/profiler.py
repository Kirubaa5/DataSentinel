import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate a basic profile of a dataset.
    """

    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": [],
    }

    for column in df.columns:
        series = df[column]

        column_profile = {
            "name": column,
            "dtype": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_percentage": float(series.isna().mean() * 100),
            "unique_count": int(series.nunique(dropna=True)),
            "duplicate_count": int(series.duplicated().sum()),
        }

        if pd.api.types.is_numeric_dtype(series):
            column_profile["min"] = (
                float(series.min()) if not series.dropna().empty else None
            )
            column_profile["max"] = (
                float(series.max()) if not series.dropna().empty else None
            )
            column_profile["mean"] = (
                float(series.mean()) if not series.dropna().empty else None
            )

        profile["columns"].append(column_profile)

    return profile