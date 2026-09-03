from datetime import datetime, timezone


def create_audit_record(
    repair_result: dict,
    before_rows: int,
    after_rows: int,
) -> dict:
    """
    Create an audit record describing a repair operation.
    """

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repair": repair_result.get("repair"),
        "approved": repair_result.get("approved", False),
        "changed": repair_result.get("changed", False),
        "before_rows": before_rows,
        "after_rows": after_rows,
        "removed_count": repair_result.get(
            "removed_count",
            0,
        ),
        "before": repair_result.get("before"),
        "after": repair_result.get("after"),
        "validation": None,
        "message": repair_result.get("message"),
    }