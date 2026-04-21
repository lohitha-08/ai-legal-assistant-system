import re


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower().strip())


def make_result(topic, intro, when_to_file, needed_details, steps, notes, rights):
    return {
        "topic": topic,
        "intro": intro,
        "when_to_file": when_to_file,
        "needed_details": needed_details,
        "steps": steps,
        "notes": notes,
        "rights": rights
    }


def get_fir_guide_answer(user_query):
    q = normalize_text(user_query)

    # 1. What is FIR
    if "what is fir" in q or q == "fir" or "fir meaning" in q:
        return make_result(
            topic="What is an FIR?",
            intro="FIR means First Information Report. It is the first official police record made when information about a cognizable offence is given to the police.",
            when_to_file="When a serious or cognizable offence like theft, assault, fraud, kidnapping, or threat takes place.",
            needed_details=[
                "Name and contact details of complainant",
                "Date and time of incident",
                "Place of incident",
                "Full description of what happened",
                "Name or description of accused if known",
                "Witness details if available",
                "Any proof like screenshots, bills, photos, videos, or medical records"
            ],
            steps=[
                "Visit the nearest police station.",
                "Explain the incident clearly in simple words.",
                "Give facts in correct order: what happened, when, where, and who was involved.",
                "Submit evidence and witness details if available.",
                "Read the complaint details carefully before final registration if shown to you.",
                "Ask for FIR number and copy after registration."
            ],
            notes=[
                "Mention only true facts.",
                "Do not hide important details.",
                "Keep a copy of FIR or acknowledgement safely for future use."
            ],
            rights="You have the right to report a cognizable offence and receive a copy of the FIR when it is registered."
        )

    # 2. How to file FIR
    elif "how to file" in q or "file fir" in q or "register fir" in q:
        return make_result(
            topic="How to File FIR",
            intro="If a cognizable offence has happened, you can file an FIR at the police station by giving a clear complaint.",
            when_to_file="As early as possible after the incident.",
            needed_details=[
                "Your name, address, and contact details",
                "Date and time of incident",
                "Exact place of incident",
                "Description of the incident",
                "Name or description of accused if known",
                "Witness names if available",
                "Supporting documents or proof"
            ],
            steps=[
                "Write the complaint clearly or explain it orally to the police officer.",
                "Mention the date, time, place, and full incident details.",
                "Provide suspect details, vehicle number, phone number, or account number if known.",
                "Submit available proof such as screenshots, photos, videos, bills, or medical reports.",
                "Ask for FIR number after registration.",
                "Take and keep a copy of the FIR safely."
            ],
            notes=[
                "Use simple and direct language.",
                "Do not wait too long without reason.",
                "Keep copies of all documents and proof."
            ],
            rights="You have the right to submit your complaint and ask for FIR details and a copy after registration."
        )

    # 3. Police refusing FIR
    elif "police not" in q or "refuse" in q or "not accepting" in q:
        return make_result(
            topic="If Police Refuse to Register FIR",
            intro="If police do not register your FIR, you can take further lawful steps.",
            when_to_file="Immediately after refusal or delay in registration.",
            needed_details=[
                "Written complaint copy",
                "Proof of incident",
                "Date and time of station visit",
                "Police station details",
                "Names of officers if known"
            ],
            steps=[
                "Keep a copy of your written complaint.",
                "Request FIR registration politely and clearly.",
                "Note the station details and date if refused.",
                "Approach a higher police officer with your complaint copy.",
                "Keep proof of follow-up communication.",
                "Seek legal support if the issue is serious."
            ],
            notes=[
                "Do not argue aggressively.",
                "Maintain written records of each attempt.",
                "Take legal aid support if necessary."
            ],
            rights="You have the right to report a cognizable offence and escalate the matter if registration is refused."
        )

    # 4. Documents needed
    elif "documents" in q or "what details" in q or "what should i bring" in q or "needed" in q:
        return make_result(
            topic="Details and Documents Needed for FIR",
            intro="While filing an FIR, clear incident details and available proof help the process.",
            when_to_file="At the time of FIR filing or complaint submission.",
            needed_details=[
                "Identity proof if available",
                "Written complaint",
                "Date, time, and place of incident",
                "Description of accused if known",
                "Proof documents or screenshots",
                "Medical records if injury is involved",
                "Witness details if available"
            ],
            steps=[
                "Prepare a short written complaint before going to the station.",
                "Carry copies of important documents.",
                "Arrange screenshots, photos, bills, or medical records clearly.",
                "Explain facts in correct order.",
                "Submit witness details if available.",
                "Ask for acknowledgement or FIR copy."
            ],
            notes=[
                "Even if all documents are not available, basic complaint can still be given.",
                "Do not submit false proof.",
                "Keep originals safe and use copies when possible."
            ],
            rights="You have the right to support your complaint with available documents and evidence."
        )

    # 5. FIR copy
    elif "fir copy" in q or "copy of fir" in q:
        return make_result(
            topic="Getting a Copy of FIR",
            intro="After FIR registration, the complainant can ask for a copy of the FIR.",
            when_to_file="Immediately after FIR is registered.",
            needed_details=[
                "FIR number if available",
                "Your complaint details",
                "Identity details if asked"
            ],
            steps=[
                "Ask the police station for the FIR copy after registration.",
                "Verify important details in the copy.",
                "Keep one photocopy and one scanned copy safely.",
                "Use the FIR number for future follow-up."
            ],
            notes=[
                "Check names, place, and incident details carefully.",
                "Store the copy safely for legal use.",
                "Do not lose the FIR number."
            ],
            rights="You have the right to receive a copy of the FIR when it is registered."
        )

    # 6. General FIR guide
    else:
        return make_result(
            topic="General FIR Guide",
            intro="An FIR is the first important step in reporting a serious offence to the police.",
            when_to_file="Usually as soon as possible after a cognizable offence.",
            needed_details=[
                "Who you are",
                "What happened",
                "When it happened",
                "Where it happened",
                "Who was involved",
                "What proof is available"
            ],
            steps=[
                "Write the incident clearly.",
                "Visit the nearest police station.",
                "Explain the matter in simple words.",
                "Submit available proof and witness details.",
                "Ask for FIR number or acknowledgement.",
                "Keep all records safely for future follow-up."
            ],
            notes=[
                "Be truthful and clear.",
                "Do not hide important facts.",
                "Take legal help if the matter is serious."
            ],
            rights="You have the right to report a cognizable offence and seek police action according to law."
        )