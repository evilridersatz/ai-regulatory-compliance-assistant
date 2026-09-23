def assess_transaction(transaction):

    text = transaction.lower()

    risk_factors = []

    # High-risk jurisdiction
    if "high-risk jurisdiction" in text or "high risk jurisdiction" in text:
        risk_factors.append(
            "High-risk jurisdiction involved"
        )

    # KYC verification
    kyc_incomplete_terms = [
        "kyc verification has not been completed",
        "kyc not completed",
        "kyc is incomplete",
        "kyc verification incomplete",
        "not kyc verified",
        "not verified"
    ]

    if "kyc" in text and any(
        term in text for term in kyc_incomplete_terms
    ):
        risk_factors.append(
            "KYC verification incomplete"
        )

    # Large transaction
    if (
        "$2 million" in text
        or "2 million" in text
        or "$2m" in text
    ):
        risk_factors.append(
            "Large cross-border transaction"
        )

    if risk_factors:
        risk_level = "HIGH"
    else:
        risk_level = "UNKNOWN"

    return {
        "risk_level": risk_level,
        "risk_factors": risk_factors
    }