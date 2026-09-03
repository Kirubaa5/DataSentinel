from typing import Any


def generate_findings(quality_results: dict) -> list[dict]:
    """
    Convert quality-check results into standardized findings.
    """

    findings = []

    # -------------------------
    # Missing values
    # -------------------------
    for result in quality_results.get("missing_values", []):
        findings.append(
            {
                "check": result["check"],
                "column": result["column"],
                "issue": "missing_values",
                "severity": result["severity"],
                "count": result["missing_count"],
                "percentage": result["missing_percentage"],
                "details": result,
            }
        )

    # -------------------------
    # Duplicate rows
    # -------------------------
    duplicate_result = quality_results.get("duplicate_rows")

    if duplicate_result:
        if duplicate_result["duplicate_count"] > 0:
            findings.append(
                {
                    "check": duplicate_result["check"],
                    "column": None,
                    "issue": "duplicate_rows",
                    "severity": duplicate_result["severity"],
                    "count": duplicate_result["duplicate_count"],
                    "percentage": duplicate_result[
                        "duplicate_percentage"
                    ],
                    "details": duplicate_result,
                }
            )

    # -------------------------
    # Data type validation
    # -------------------------
    for result in quality_results.get(
        "data_type_validation", []
    ):
        findings.append(
            {
                "check": result["check"],
                "column": result["column"],
                "issue": result.get(
                    "issue",
                    "unexpected_data_type",
                ),
                "severity": result["severity"],
                "count": result.get(
                    "unexpected_count",
                    None,
                ),
                "percentage": result.get(
                    "unexpected_percentage",
                    None,
                ),
                "details": result,
            }
        )

    # -------------------------
    # Outliers
    # -------------------------
    for result in quality_results.get("outliers", []):
        if result["outlier_count"] > 0:
            findings.append(
                {
                    "check": result["check"],
                    "column": result["column"],
                    "issue": "outliers",
                    "severity": result["severity"],
                    "count": result["outlier_count"],
                    "percentage": result[
                        "outlier_percentage"
                    ],
                    "details": result,
                }
            )

    return findings