def get_evidence_help(user_input):
    text = user_input.lower()

    # Theft case
    if "theft" in text or "stolen" in text or "mobile" in text:
        return {
            "title": "Theft Case",
            "documents": [
                "ID proof",
                "Purchase bill",
                "Mobile IMEI number"
            ],
            "evidence": [
                "CCTV footage",
                "Witness details",
                "Photo of stolen item"
            ],
            "missing": [
                "Incident date not mentioned",
                "Location details missing"
            ],
            "note": "Keep original documents safe and submit only copies if required."
        }

    # Fraud case
    elif "fraud" in text or "scam" in text:
        return {
            "title": "Fraud Case",
            "documents": [
                "ID proof",
                "Bank statement",
                "Transaction receipt"
            ],
            "evidence": [
                "Screenshots",
                "Call recordings",
                "Transaction ID"
            ],
            "missing": [
                "Exact transaction date missing"
            ],
            "note": "Report immediately to cyber crime portal."
        }

    # Default
    else:
        return {
            "title": "General Case",
            "documents": [
                "ID proof",
                "Any supporting documents"
            ],
            "evidence": [
                "Photos",
                "Witness",
                "Screenshots"
            ],
            "missing": [],
            "note": "Provide clear details for better help."
        }