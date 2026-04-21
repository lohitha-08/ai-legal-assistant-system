import re


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower().strip())


def make_result(topic, law_reference, intro, punishment, next_steps, evidence, rights_summary):
    return {
        "topic": topic,
        "law_reference": law_reference,
        "intro": intro,
        "punishment": punishment,
        "next_steps": next_steps,
        "evidence": evidence,
        "rights_summary": rights_summary
    }


def get_rights_answer(user_query):
    q = normalize_text(user_query)

    if "arrest" in q or "custody" in q or "police arrested" in q:
        return make_result(
            topic="Arrest Rights",
            law_reference="Criminal procedure safeguards apply during arrest",
            intro="A person has certain legal protections during arrest and police custody.",
            punishment="Depends on the offence involved, not on arrest alone.",
            next_steps=[
                "Stay calm and ask the reason for arrest.",
                "Ask under which case or section you are being arrested.",
                "Contact a lawyer or inform a family member immediately.",
                "Do not sign anything without understanding it."
            ],
            evidence=[
                "Arrest memo details if available",
                "Police station name",
                "Case or FIR number",
                "Names of officers if known"
            ],
            rights_summary="You have the right to know the grounds of arrest, contact a lawyer or family member, and be produced before the magistrate within the legal time limit."
        )

    elif "women" in q or "woman" in q or "female" in q:
        return make_result(
            topic="Women Rights",
            law_reference="Domestic Violence Act / POSH Act / IPC protections",
            intro="Women are protected under various laws for safety, dignity, and equality.",
            punishment="As per law",
            next_steps=[
                "Approach the nearest police station or women help desk.",
                "Explain the issue clearly and give all available details.",
                "Submit proof such as messages, photos, videos, or medical records if available.",
                "Ask for complaint acknowledgement and keep a copy safely."
            ],
            evidence=[
                "Messages or screenshots",
                "Photos or videos",
                "Medical reports if injury exists",
                "Witness details",
                "Complaint copy"
            ],
            rights_summary="Women have the right to dignity, privacy, safety, legal protection, and support against harassment, violence, and abuse."
        )

    elif "consumer" in q or "product" in q or "refund" in q or "bill" in q:
        return make_result(
            topic="Consumer Rights",
            law_reference="Consumer protection laws apply in defective goods and unfair trade practices",
            intro="Consumers have legal protection against defective products, poor service, fake promises, and unfair trade practices.",
            punishment="Depends on consumer forum decision and type of violation.",
            next_steps=[
                "Keep the bill, warranty card, and proof of purchase safely.",
                "Contact the seller or service provider first.",
                "Submit a written complaint with issue details.",
                "Approach the consumer forum if the issue is not resolved."
            ],
            evidence=[
                "Bill or invoice",
                "Warranty card",
                "Product photos",
                "Chats, emails, or complaint copies"
            ],
            rights_summary="Consumers have the right to safety, information, complaint, and compensation in proper cases."
        )

    elif "cyber" in q or "online" in q or "hack" in q or "fake account" in q:
        return make_result(
            topic="Cyber Rights",
            law_reference="IT Act and related legal protections may apply",
            intro="You have legal rights against online fraud, fake accounts, hacking, digital abuse, and privacy violations.",
            punishment="Punishment depends on the cyber offence and applicable legal provisions.",
            next_steps=[
                "Take screenshots immediately.",
                "Save links, account names, numbers, and digital details.",
                "Change passwords if account misuse is involved.",
                "Report through cybercrime portal or police station."
            ],
            evidence=[
                "Screenshots",
                "Transaction details",
                "Emails or messages",
                "Fake profile or page links"
            ],
            rights_summary="You have the right to report cybercrime, seek investigation, and use digital evidence for protection."
        )

    elif "child" in q or "minor" in q or "kid" in q:
        return make_result(
            topic="Child Rights",
            law_reference="Child protection laws apply in abuse, neglect, and exploitation cases",
            intro="Children have special legal protection against abuse, exploitation, neglect, and unsafe conditions.",
            punishment="Punishment depends on the nature of offence against the child.",
            next_steps=[
                "Ensure the child is in a safe place.",
                "Inform police or child protection authority.",
                "Seek medical help if needed.",
                "Keep records of abuse or threat safely."
            ],
            evidence=[
                "Medical reports",
                "Photos or videos if available",
                "Messages or call proof",
                "Witness details"
            ],
            rights_summary="A child has the right to safety, care, dignity, protection, and immediate legal support."
        )

    else:
        return make_result(
            topic="General Legal Rights",
            law_reference="Basic legal rights and protections apply",
            intro="Every citizen has certain legal rights such as equality before law, fair treatment, and access to legal remedies.",
            punishment="Depends on the actual legal issue involved.",
            next_steps=[
                "Write down your issue clearly.",
                "Collect available proof and documents.",
                "Approach the proper authority or police station.",
                "Seek legal guidance if the matter is serious."
            ],
            evidence=[
                "Identity proof",
                "Complaint copy",
                "Messages or screenshots",
                "Photos, videos, or witness details"
            ],
            rights_summary="You have the right to legal help, fair treatment, complaint filing, and access to justice."
        )