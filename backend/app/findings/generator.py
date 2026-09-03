def generate_findings(quality_results: dict) -> list[dict]:
    """
    Convert quality-check results into standardized findings.
    """

    findings = []

    def add_finding(result: dict, issue: str, count_key: str, percentage_key: str) -> None:
        count = int(result.get(count_key, 0))
        if count <= 0:
            return
        findings.append({
            "finding_id": f"{result['check']}:{result.get('column') or 'dataset'}",
            "check": result["check"],
            "column": result.get("column"),
            "issue": issue,
            "severity": result.get("severity", "low"),
            "count": count,
            "percentage": result.get(percentage_key),
            "details": result,
        })

    # -------------------------
    # Missing values
    # -------------------------
    for result in quality_results.get("missing_values", []):
        add_finding(result, "missing_values", "missing_count", "missing_percentage")

    # -------------------------
    # Duplicate rows
    # -------------------------
    duplicate_result = quality_results.get("duplicate_rows")

    if duplicate_result:
        if duplicate_result["duplicate_count"] > 0:
            add_finding(duplicate_result, "duplicate_rows", "duplicate_count", "duplicate_percentage")

    # -------------------------
    # Data type validation
    # -------------------------
    for result in quality_results.get(
        "data_type_validation", []
    ):
        add_finding(result, result.get("issue", "unexpected_data_type"), "unexpected_count", "unexpected_percentage")

    # -------------------------
    # Outliers
    # -------------------------
    for result in quality_results.get("outliers", []):
        if result["outlier_count"] > 0:
            add_finding(result, "outliers", "outlier_count", "outlier_percentage")

    for result in quality_results.get("numeric_constraints", []):
        add_finding(result, "numeric_constraint", "invalid_count", "invalid_percentage")
    for result in quality_results.get("format_validation", []):
        add_finding(result, "format_validation", "invalid_count", "invalid_percentage")

    return findings