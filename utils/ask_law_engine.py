import re


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower().strip())


def make_result(title, section, explanation, punishment, next_steps, evidence, rights):
    return {
        "title": title,
        "section": section,
        "explanation": explanation,
        "punishment": punishment,
        "next_steps": next_steps,
        "evidence": evidence,
        "rights": rights
    }


def get_ask_law_answer(user_query):
    q = normalize_text(user_query)

    if any(word in q for word in ["theft", "stolen", "steal", "rob", "robbery"]):
        return make_result(
            title="Theft Guidance",
            section="IPC 378 / 379 – Theft",
            explanation="Theft means taking someone else's movable property dishonestly without permission.",
            punishment="Possible punishment may extend up to 3 years imprisonment, or fine, or both.",
            next_steps=[
                "Go to the nearest police station and file a complaint or FIR.",
                "Give full details of the stolen item.",
                "Mention place, time, and suspect details if known.",
                "Keep a copy of the complaint for follow-up."
            ],
            evidence=[
                "Purchase bill or ownership proof",
                "Photos of item",
                "CCTV footage if available",
                "Witness details"
            ],
            rights="You have the right to submit a complaint and receive acknowledgement."
        )

    elif any(word in q for word in ["fraud", "cheat", "cheated", "scam"]):
        return make_result(
            title="Fraud / Cheating Guidance",
            section="IPC 420 – Cheating and Fraud",
            explanation="Fraud or cheating happens when someone dishonestly deceives you and causes loss of money or property.",
            punishment="Possible punishment may extend up to 7 years imprisonment and fine.",
            next_steps=[
                "Collect all transaction proofs and communication records.",
                "File a complaint at the police station or cybercrime portal.",
                "Give account, UPI, mobile number, and transaction details.",
                "Keep complaint number for tracking."
            ],
            evidence=[
                "Payment screenshots",
                "Bank statements",
                "UPI transaction IDs",
                "Chat messages / email proof"
            ],
            rights="You have the right to report cheating and seek police help."
        )

    elif any(word in q for word in ["assault", "attack", "hit", "beaten", "fight"]):
        return make_result(
            title="Assault Guidance",
            section="IPC 351 / 352 – Assault or Criminal Force",
            explanation="Assault generally means using criminal force or threatening immediate physical harm.",
            punishment="Punishment depends on injury and facts of the case.",
            next_steps=[
                "Get medical help immediately if injured.",
                "Take medical records or wound certificate.",
                "File a police complaint.",
                "Mention names of witnesses and place of incident."
            ],
            evidence=[
                "Medical certificate",
                "Photos of injuries",
                "Witness statements",
                "CCTV footage"
            ],
            rights="You have the right to medical treatment and police protection."
        )

    elif any(word in q for word in ["threat", "threaten", "blackmail", "intimidate"]):
        return make_result(
            title="Threat / Intimidation Guidance",
            section="IPC 503 / 506 – Criminal Intimidation",
            explanation="Threatening a person with harm or pressure may amount to criminal intimidation.",
            punishment="Punishment depends on seriousness of the threat.",
            next_steps=[
                "Do not delete messages or proof.",
                "Avoid direct confrontation if unsafe.",
                "File a complaint at the nearest police station.",
                "Explain what threat was made and by whom."
            ],
            evidence=[
                "Threat messages",
                "Screenshots",
                "Audio recordings",
                "Call history"
            ],
            rights="You have the right to seek police protection and legal remedy."
        )

    elif any(word in q for word in ["harassment", "harass", "stalking", "abuse"]):
        return make_result(
            title="Harassment Guidance",
            section="Relevant IPC provisions depend on the facts of the case",
            explanation="Harassment can include repeated abuse, stalking, intimidation, or mental cruelty.",
            punishment="Punishment depends on the exact act and legal section.",
            next_steps=[
                "Write down incidents with date and place.",
                "Save messages, calls, images, or recordings.",
                "Report the matter to police or authority.",
                "Keep complaint copies safely."
            ],
            evidence=[
                "Chats and emails",
                "Audio / video proof",
                "Witness statements",
                "Complaint copies"
            ],
            rights="You have the right to dignity, safety, and legal protection."
        )

    elif any(word in q for word in ["cyber", "hacked", "hack", "otp fraud", "fake account"]):
        return make_result(
            title="Cyber Crime Guidance",
            section="IT Act Section 66 and related IPC provisions may apply",
            explanation="Cyber crime includes hacking, fake profiles, OTP fraud, online cheating, or identity misuse.",
            punishment="Punishment depends on the type of cyber offence.",
            next_steps=[
                "Take screenshots immediately.",
                "Change passwords and secure your accounts.",
                "Report through cybercrime portal or nearest police station.",
                "Provide all digital details involved."
            ],
            evidence=[
                "Screenshots",
                "Transaction IDs",
                "Messages / emails",
                "Fake profile links"
            ],
            rights="You have the right to report cyber offences using digital evidence."
        )

    elif any(word in q for word in ["domestic violence", "dowry harassment", "family abuse"]):
        return make_result(
            title="Domestic Violence Guidance",
            section="Protection of Women from Domestic Violence Act, 2005 and related IPC provisions may apply",
            explanation="Domestic violence includes physical, emotional, verbal, or economic abuse within a domestic relationship.",
            punishment="Legal action depends on the nature of abuse and applicable law.",
            next_steps=[
                "Move to a safe place if there is immediate danger.",
                "Inform police or trusted support person.",
                "Keep medical records and proof of abuse.",
                "Seek legal assistance."
            ],
            evidence=[
                "Medical reports",
                "Photos of injuries",
                "Threat messages",
                "Witness details"
            ],
            rights="Victim has the right to protection, legal remedy, and police assistance."
        )

    elif any(word in q for word in ["fir", "file fir", "fir help", "police not accepting complaint"]):
        return make_result(
            title="FIR Help",
            section="CrPC-related procedure applies for FIR registration",
            explanation="An FIR is the first official police record of a cognizable offence.",
            punishment="Punishment depends on the offence mentioned in the FIR.",
            next_steps=[
                "Visit police station and explain incident clearly.",
                "Give date, time, place, and accused details.",
                "Ask for FIR number or acknowledgement.",
                "If refused, escalate to higher authority."
            ],
            evidence=[
                "Written complaint",
                "Identity proof",
                "Incident proof documents",
                "Witness details"
            ],
            rights="You have the right to submit information and receive a copy of FIR when registered."
        )

    elif any(word in q for word in ["bail", "anticipatory bail", "regular bail", "bailable", "non bailable"]):
        return make_result(
            title="Bail Information",
            section="Bail depends on whether the offence is bailable or non-bailable",
            explanation="Bail means temporary release of an accused person under legal conditions.",
            punishment="Punishment depends on the actual offence, not on bail itself.",
            next_steps=[
                "Understand the section involved in the case.",
                "Check whether offence is bailable or non-bailable.",
                "Approach lawyer or court with case documents.",
                "Follow court conditions if bail is granted."
            ],
            evidence=[
                "FIR copy",
                "Case number",
                "Identity proof",
                "Supporting documents"
            ],
            rights="An accused person has legal rights, including the right to seek bail."
        )

    elif any(word in q for word in ["arrest", "arrest rights", "custody rights", "taken by police"]):
        return make_result(
            title="Arrest Rights Guidance",
            section="Arrest-related legal safeguards apply under criminal procedure law",
            explanation="A person arrested by police has certain legal protections and procedural rights.",
            punishment="Punishment is not decided by arrest alone.",
            next_steps=[
                "Stay calm and ask the reason for arrest.",
                "Ask under which section you are being arrested.",
                "Inform a family member or lawyer immediately.",
                "Do not sign anything without understanding it."
            ],
            evidence=[
                "Arrest memo details",
                "Police station details",
                "Case or FIR number",
                "Names of officers"
            ],
            rights="A person has the right to know the grounds of arrest and contact a lawyer or family member."
        )

    else:
        return make_result(
            title="General Legal Guidance",
            section="Relevant IPC / legal section needs review",
            explanation="Your issue does not clearly match one single category. A more detailed legal review may be required based on full facts.",
            punishment="Punishment cannot be identified exactly until the correct legal section is determined.",
            next_steps=[
                "Write your issue clearly with date, place, and persons involved.",
                "Collect documents, messages, screenshots, photos, or records.",
                "Approach the nearest police station or legal aid service.",
                "Keep copies of every complaint and submission."
            ],
            evidence=[
                "Complaint copy",
                "Messages / screenshots",
                "Photos / videos",
                "Identity proof",
                "Witness details"
            ],
            rights="You have the right to legal guidance, fair treatment, and to submit a complaint."
        )