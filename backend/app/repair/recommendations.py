def generate_recommendations(
    findings: list[dict],
    business_rules: list[dict],
) -> list[dict]:
    """
    Generate safe remediation recommendations from findings
    and business-rule classifications.
    """

    recommendations = []

    # Rules that represent expected business behavior
    expected_rules = {
        rule["rule"]
        for rule in business_rules
        if rule.get("classification")
        == "expected_business_behavior"
    }

    for finding in findings:

        check = finding.get("check")
        column = finding.get("column")
        severity = finding.get("severity")

        # --------------------------------------------
        # Missing values
        # --------------------------------------------
        if check == "missing_values":

            if severity == "critical":
                action = "human_review"
                reason = (
                    "High-impact missing values require "
                    "business review before modification."
                )

            elif severity in {"high", "medium"}:
                action = "investigate"
                reason = (
                    "Review the missing-value pattern before "
                    "choosing an imputation or removal strategy."
                )

            else:
                action = "investigate"
                reason = (
                    "Small amounts of missing data may be "
                    "handled depending on column importance."
                )

        # --------------------------------------------
        # Duplicate rows
        # --------------------------------------------
        elif check == "duplicate_rows":

            action = "review_duplicates"

            reason = (
                "Duplicate rows should be reviewed before "
                "removal because repeated transactions may "
                "sometimes be legitimate."
            )

        # --------------------------------------------
        # Data type validation
        # --------------------------------------------
        elif check == "data_type_validation":

            action = "standardize_type"

            reason = (
                "Mixed data types should be standardized "
                "after verifying the intended column type."
            )

        # --------------------------------------------
        # Outliers
        # --------------------------------------------
        elif check == "iqr_outlier":

            action = "investigate_outliers"

            reason = (
                "Statistical outliers are not automatically "
                "errors and should be investigated before "
                "changing their values."
            )

        else:
            action = "investigate"
            reason = (
                "Review the finding before applying an "
                "automated correction."
            )

        recommendations.append(
            {
                "check": check,
                "column": column,
                "severity": severity,
                "action": action,
                "reason": reason,
                "safe_to_auto_repair": False,
            }
        )

    # --------------------------------------------
    # Business-rule recommendation
    # --------------------------------------------
    if "legitimate_return_quantity" in expected_rules:

        recommendations.append(
            {
                "check": "business_rule",
                "column": "Quantity",
                "severity": "none",
                "action": "keep_value",
                "reason": (
                    "Negative quantities associated with "
                    "cancellation invoices represent expected "
                    "return/cancellation behavior."
                ),
                "safe_to_auto_repair": False,
            }
        )

    return recommendations