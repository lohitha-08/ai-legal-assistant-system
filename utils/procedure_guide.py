import re


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower().strip())


def make_result(title, intro, steps, tips):
    return {
        "title": title,
        "intro": intro,
        "steps": steps,
        "tips": tips
    }


def get_procedure_answer(user_input):
    q = normalize_text(user_input)

    if any(word in q for word in ["theft", "stolen", "steal", "robbery", "phone stolen", "bike stolen"]):
        return make_result(
            title="Steps for Theft Complaint",
            intro="If your phone, bike, money, or other property is stolen, follow these steps.",
            steps=[
                "Stay calm and note the exact time and place of theft.",
                "Collect proof of ownership like bill, IMEI number, or registration certificate.",
                "Visit the nearest police station and file a complaint or FIR.",
                "Provide item details, suspect details, and witness information if available.",
                "Ask for complaint acknowledgement or FIR copy.",
                "Follow up with police using complaint number."
            ],
            tips=[
                "Do not delay complaint filing.",
                "Keep photocopies of all submitted documents.",
                "Block SIM or bank account quickly if relevant."
            ]
        )

    elif any(word in q for word in ["fraud", "cheat", "scam", "online fraud", "money cheated"]):
        return make_result(
            title="Steps for Fraud / Cheating Case",
            intro="If someone cheated you in money or online transaction, do this step by step.",
            steps=[
                "Save transaction screenshots, UPI IDs, call logs, and messages.",
                "Write down the full incident clearly with date and time.",
                "Report immediately to cybercrime portal if online fraud is involved.",
                "Also file a complaint at the nearest police station.",
                "Share bank details, account numbers, links, and suspect information.",
                "Keep complaint reference number safe for tracking."
            ],
            tips=[
                "Fast reporting improves chances of recovery.",
                "Do not share OTP or passwords with anyone.",
                "Keep all digital proofs untouched."
            ]
        )

    elif any(word in q for word in ["assault", "attack", "hit", "beaten", "violence", "fight"]):
        return make_result(
            title="Steps for Assault Case",
            intro="If someone physically attacked or harmed you, follow these steps carefully.",
            steps=[
                "Move to a safe place immediately.",
                "Get medical treatment and ask for medical records.",
                "Take photos of injuries if possible.",
                "Visit the police station and file a complaint or FIR.",
                "Give full details of the incident and accused person if known.",
                "Submit names of witnesses and available proof."
            ],
            tips=[
                "Medical proof is very important.",
                "Do not hide serious injuries.",
                "File complaint as early as possible."
            ]
        )

    elif any(word in q for word in ["threat", "threaten", "blackmail", "intimidate"]):
        return make_result(
            title="Steps for Threat / Blackmail Complaint",
            intro="If someone is threatening or blackmailing you, use this process.",
            steps=[
                "Save all threatening messages, calls, screenshots, or recordings.",
                "Do not delete evidence.",
                "Avoid direct confrontation if you feel unsafe.",
                "Write down what happened, when, and who made the threat.",
                "File a police complaint with complete details.",
                "Seek protection if the threat is serious."
            ],
            tips=[
                "Evidence is the strongest support in threat cases.",
                "Tell a trusted family member or friend.",
                "Act quickly in serious threat situations."
            ]
        )

    elif any(word in q for word in ["harassment", "stalking", "abuse", "mental torture"]):
        return make_result(
            title="Steps for Harassment Complaint",
            intro="If you are facing harassment, stalking, or repeated abuse, follow these steps.",
            steps=[
                "Write down each incident with date, place, and what happened.",
                "Save chats, emails, screenshots, recordings, or photos.",
                "If workplace-related, report to internal authority if available.",
                "Visit the nearest police station and file a complaint.",
                "Submit proof and witness details if any.",
                "Keep copies of complaint and follow-up records."
            ],
            tips=[
                "Repeated incidents should be documented properly.",
                "Do not ignore continued harassment.",
                "Take support from trusted people if needed."
            ]
        )

    elif any(word in q for word in ["cyber", "hack", "fake account", "otp fraud", "online abuse"]):
        return make_result(
            title="Steps for Cyber Crime Complaint",
            intro="If your problem is online hacking, fake account, OTP fraud, or cyber abuse, do this.",
            steps=[
                "Take screenshots of messages, accounts, links, and transactions.",
                "Change passwords immediately.",
                "Secure email, bank, and social media accounts.",
                "Report the issue on the cybercrime portal.",
                "File complaint at nearest police station if needed.",
                "Keep complaint number and copies of proofs."
            ],
            tips=[
                "Time matters in cybercrime reporting.",
                "Never share OTP or password.",
                "Keep digital evidence safe and clear."
            ]
        )

    elif any(word in q for word in ["domestic violence", "family abuse", "dowry harassment", "home violence"]):
        return make_result(
            title="Steps for Domestic Violence Case",
            intro="If you are facing abuse at home, your safety comes first. Follow these steps.",
            steps=[
                "Move to a safe place if there is immediate danger.",
                "Contact police or trusted support person.",
                "Take medical help if injured.",
                "Save photos, messages, and records of abuse.",
                "File complaint with police or concerned authority.",
                "Seek legal protection and support services."
            ],
            tips=[
                "Your safety is the first priority.",
                "Keep emergency contacts ready.",
                "Do not stay silent in serious abuse situations."
            ]
        )

    elif any(word in q for word in ["fir", "file fir", "police complaint", "complaint not accepted"]):
        return make_result(
            title="Steps to File FIR / Police Complaint",
            intro="If you want to file an FIR or complaint, this is the simple process.",
            steps=[
                "Write the incident clearly with date, time, and place.",
                "Visit the police station with your written complaint.",
                "Explain the incident clearly to the officer.",
                "Submit any available proof or witness details.",
                "Ask for FIR number or complaint acknowledgement.",
                "Keep a copy for future follow-up."
            ],
            tips=[
                "Use clear and simple language.",
                "Mention only true facts.",
                "Keep all proof documents ready."
            ]
        )

    else:
        return make_result(
            title="General Step-by-Step Guide",
            intro="Follow these common legal action steps for most basic complaint situations.",
            steps=[
                "Write your issue clearly with date, time, and place.",
                "Collect available evidence like documents, screenshots, or witness details.",
                "Visit the nearest police station or legal authority.",
                "Submit your complaint clearly and politely.",
                "Ask for acknowledgement or complaint copy.",
                "Keep records for follow-up."
            ],
            tips=[
                "Do not delay important complaints.",
                "Keep copies of all records.",
                "Ask legal help if the matter is serious."
            ]
        )