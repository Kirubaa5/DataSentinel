from pathlib import Path

import pandas as pd

from app.ingestion.validators import validate_file_path


def load_dataset(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV or Excel dataset and reject empty inputs."""
    path = validate_file_path(file_path)
    if path.suffix.lower() == ".csv":
        dataframe = pd.read_csv(path)
    else:
        dataframe = pd.read_excel(path)

    if dataframe.empty or dataframe.dropna(how="all").empty:
        raise ValueError(f"Dataset contains no rows: {path}")
    return dataframe
