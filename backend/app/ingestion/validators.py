from pathlib import Path


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_file_path(file_path: str | Path) -> Path:
	"""Return a validated dataset path."""
	path = Path(file_path)
	if not path.exists():
		raise FileNotFoundError(f"Dataset file does not exist: {path}")
	if not path.is_file():
		raise ValueError(f"Dataset path is not a file: {path}")
	if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
		supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
		raise ValueError(f"Unsupported dataset format '{path.suffix}'. Use: {supported}")
	return path
