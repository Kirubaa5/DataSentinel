def calculate_quality_score(findings: list[dict]) -> dict:
    """
    Calculate a deterministic 0-100 data quality score
    based on finding severity.
    """

    severity_penalties = {
        "critical": 20,
        "high": 10,
        "medium": 5,
        "low": 2,
    }

    score = 100

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    total_penalty = 0

    for finding in findings:
        severity = finding.get("severity", "low")

        if severity not in severity_penalties:
            continue

        severity_counts[severity] += 1

        total_penalty += severity_penalties[severity]

    score = max(0, score - total_penalty)

    if score >= 90:
        grade = "excellent"
    elif score >= 75:
        grade = "good"
    elif score >= 50:
        grade = "fair"
    elif score >= 25:
        grade = "poor"
    else:
        grade = "critical"

    return {
        "score": score,
        "grade": grade,
        "total_findings": len(findings),
        "total_penalty": total_penalty,
        "severity_counts": severity_counts,
    }