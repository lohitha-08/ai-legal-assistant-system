import random

def summarize_case(text):

    # simple summarization (demo)
    summary = text[:400]

    return summary


def predict_ipc(text):

    text = text.lower()

    if "murder" in text:
        return "IPC Section 302 - Murder"

    elif "theft" in text:
        return "IPC Section 379 - Theft"

    elif "fraud" in text or "cheating" in text:
        return "IPC Section 420 - Cheating"

    elif "assault" in text:
        return "IPC Section 351 - Assault"

    else:
        return "IPC Section Prediction Uncertain"


def evidence_strength(text):

    words = text.lower()

    if "video" in words or "cctv" in words or "recording" in words:
        return "High"

    elif "witness" in words:
        return "Medium"

    else:
        return "Low"


def legal_risk(text):

    if "murder" in text.lower():
        return "High"

    elif "fraud" in text.lower():
        return "Medium"

    else:
        return "Low"


def punishment(ipc):

    punishments = {
        "IPC Section 302 - Murder": "Life Imprisonment or Death",
        "IPC Section 379 - Theft": "Up to 3 years imprisonment",
        "IPC Section 420 - Cheating": "Up to 7 years imprisonment",
        "IPC Section 351 - Assault": "Up to 3 months imprisonment"
    }

    return punishments.get(ipc, "Punishment depends on court judgement")