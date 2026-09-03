import pandas as pd


def apply_business_rules(df: pd.DataFrame) -> list[dict]:
    """
    Apply business-context rules to a dataset.

    Returns findings that require business interpretation.
    """

    findings = []

    # --------------------------------------------------
    # Rule 1: Negative quantity with cancellation invoice
    # --------------------------------------------------
    if "InvoiceNo" in df.columns and "Quantity" in df.columns:

        invoice_values = df["InvoiceNo"].astype(str)
        quantity_values = pd.to_numeric(
            df["Quantity"],
            errors="coerce",
        )

        return_mask = (
            invoice_values.str.startswith("C")
            & (quantity_values < 0)
        )

        return_count = int(return_mask.sum())

        if return_count > 0:
            findings.append(
                {
                    "rule": "legitimate_return_quantity",
                    "columns": ["InvoiceNo", "Quantity"],
                    "classification": "expected_business_behavior",
                    "affected_count": return_count,
                    "message": (
                        "Negative quantities associated with "
                        "cancellation invoices are treated as "
                        "legitimate returns/cancellations."
                    ),
                }
            )

    return findings