

def suggest_ipc(user_input):
    text = (user_input or "").lower().strip()

    if "theft" in text or "stolen" in text or "mobile" in text or "bike" in text:
        return {
            "title": "Theft",
            "section": "IPC 379",
            "description": "Taking someone's property without permission.",
            "punishment": "Up to 3 years imprisonment or fine or both"
        }

    elif "fraud" in text or "scam" in text or "cheating" in text:
        return {
            "title": "Cheating / Fraud",
            "section": "IPC 420",
            "description": "Cheating someone for money or benefit.",
            "punishment": "Up to 7 years imprisonment and fine"
        }

    elif "murder" in text or "kill" in text:
        return {
            "title": "Murder",
            "section": "IPC 302",
            "description": "Causing death intentionally.",
            "punishment": "Death penalty or life imprisonment"
        }

    elif "harassment" in text or "molest" in text:
        return {
            "title": "Outraging Modesty",
            "section": "IPC 354",
            "description": "Assault or criminal force against a woman.",
            "punishment": "Up to 5 years imprisonment and fine"
        }

    else:
        return {
            "title": "General Law Help",
            "section": "-",
            "description": "Please describe your problem clearly.",
            "punishment": "-"
        }