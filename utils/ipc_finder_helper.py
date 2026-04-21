import re


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower().strip())


def make_result(section, offense, explanation, punishment, next_steps):
    return {
        "section": section,
        "offense": offense,
        "explanation": explanation,
        "punishment": punishment,
        "next_steps": next_steps
    }


def get_ipc_finder_answer(user_query):
    q = normalize_text(user_query)

    if any(word in q for word in ["theft", "stolen", "steal", "robbery", "bike stolen", "phone stolen"]):
        return make_result(
            section="IPC 378 / 379",
            offense="Theft",
            explanation="Theft means taking movable property dishonestly without the owner's permission.",
            punishment="Punishment may extend up to 3 years imprisonment, or fine, or both.",
            next_steps=[
                "File a police complaint or FIR.",
                "Collect ownership proof such as bill or registration.",
                "Submit witness details or CCTV proof if available."
            ]
        )

    elif any(word in q for word in ["fraud", "cheat", "cheated", "scam", "money cheated"]):
        return make_result(
            section="IPC 420",
            offense="Cheating / Fraud",
            explanation="Cheating means deceiving a person dishonestly and causing wrongful loss.",
            punishment="Punishment may extend up to 7 years imprisonment and fine.",
            next_steps=[
                "Collect payment proof, chats, call logs, and screenshots.",
                "File complaint at police station or cybercrime portal.",
                "Keep transaction details safely."
            ]
        )

    elif any(word in q for word in ["assault", "attack", "hit", "beaten", "fight"]):
        return make_result(
            section="IPC 351 / 352",
            offense="Assault / Criminal Force",
            explanation="Assault generally involves use of criminal force or threat of physical harm.",
            punishment="Punishment depends on injury and facts, and may include imprisonment or fine.",
            next_steps=[
                "Take medical treatment immediately if injured.",
                "Collect medical proof and photos.",
                "File police complaint with incident details."
            ]
        )

    elif any(word in q for word in ["threat", "threaten", "blackmail", "intimidate"]):
        return make_result(
            section="IPC 503 / 506",
            offense="Criminal Intimidation",
            explanation="Threatening a person with injury, harm, or pressure may amount to criminal intimidation.",
            punishment="Punishment depends on seriousness of threat and circumstances.",
            next_steps=[
                "Save threat messages, recordings, or screenshots.",
                "Avoid direct confrontation if unsafe.",
                "File complaint with police."
            ]
        )

    elif any(word in q for word in ["cyber", "hack", "fake account", "otp fraud", "online fraud"]):
        return make_result(
            section="IT Act Section 66 + related IPC provisions",
            offense="Cyber Crime",
            explanation="Cyber crime includes hacking, fake profiles, OTP fraud, or online misuse.",
            punishment="Punishment depends on type of cyber offence and legal provisions applied.",
            next_steps=[
                "Take screenshots immediately.",
                "Change passwords if needed.",
                "Report through cybercrime portal or nearest police station."
            ]
        )

    elif any(word in q for word in ["domestic violence", "family abuse", "dowry harassment"]):
        return make_result(
            section="Protection of Women from Domestic Violence Act + related IPC provisions",
            offense="Domestic Violence",
            explanation="Domestic violence includes physical, emotional, verbal, or economic abuse in a domestic relationship.",
            punishment="Action depends on type of abuse and sections involved.",
            next_steps=[
                "Move to a safe place if in danger.",
                "Keep medical and message proof.",
                "Seek police or legal support immediately."
            ]
        )

    else:
        return make_result(
            section="Relevant section needs detailed legal review",
            offense="General Legal Issue",
            explanation="Your issue does not match one exact category clearly. More facts may be needed.",
            punishment="Punishment depends on actual legal section involved.",
            next_steps=[
                "Write down complete incident details.",
                "Collect all documents and proof.",
                "Approach police station or legal expert for proper section identification."
            ]
        )