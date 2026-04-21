# utils/complaint_draft_engine.py

def generate_complaint_draft(form_data):
    name = (form_data.get("name") or "").strip()
    father_name = (form_data.get("father_name") or "").strip()
    address = (form_data.get("address") or "").strip()
    phone = (form_data.get("phone") or "").strip()
    incident_date = (form_data.get("incident_date") or "").strip()
    incident_time = (form_data.get("incident_time") or "").strip()
    incident_place = (form_data.get("incident_place") or "").strip()
    complaint_type = (form_data.get("complaint_type") or "").strip()
    accused_details = (form_data.get("accused_details") or "").strip()
    description = (form_data.get("description") or "").strip()
    evidence = (form_data.get("evidence") or "").strip()

    subject_map = {
        "theft": "Complaint regarding theft incident",
        "fraud": "Complaint regarding cheating / fraud incident",
        "harassment": "Complaint regarding harassment",
        "cyber": "Complaint regarding cyber crime",
        "assault": "Complaint regarding assault incident",
        "domestic": "Complaint regarding domestic violence",
        "missing_item": "Complaint regarding missing property",
        "other": "Complaint regarding incident"
    }

    subject = subject_map.get(complaint_type, "Complaint regarding incident")

    intro_name = name if name else "the undersigned"
    father_line = f", S/o or D/o {father_name}" if father_name else ""
    address_line = f", residing at {address}" if address else ""
    phone_line = f". My contact number is {phone}" if phone else ""
    date_line = incident_date if incident_date else "__________"
    time_line = incident_time if incident_time else "__________"
    place_line = incident_place if incident_place else "__________"
    accused_line = accused_details if accused_details else "Unknown / Not specified"
    evidence_line = evidence if evidence else "No specific evidence details provided"

    body = f"""To
The Station House Officer,
[Police Station Name],
[City / District]

Subject: {subject}

Respected Sir/Madam,

I, {intro_name}{father_line}{address_line}{phone_line}, respectfully submit this complaint for your kind action.

I would like to inform you that on {date_line} at about {time_line}, an incident related to {complaint_type if complaint_type else 'the matter described below'} took place at {place_line}.

Brief facts of the complaint:
{description if description else "The incident details have not been fully provided."}

Accused / Suspect Details:
{accused_line}

Available Documents / Evidence:
{evidence_line}

I request you to kindly take necessary legal action on this complaint and do the needful as per law. I am ready to cooperate with the investigation and provide any further details if required.

Thanking you,

Yours faithfully,
{name if name else "Complainant"}

Name: {name if name else "__________"}
Father / Mother Name: {father_name if father_name else "__________"}
Address: {address if address else "__________"}
Phone: {phone if phone else "__________"}
Date: {incident_date if incident_date else "__________"}
Place: {incident_place if incident_place else "__________"}
"""

    missing = []

    if not name:
        missing.append("Complainant name is missing")
    if not incident_date:
        missing.append("Incident date is missing")
    if not incident_place:
        missing.append("Incident place is missing")
    if not description:
        missing.append("Complaint description is missing")

    return {
        "subject": subject,
        "draft": body,
        "missing": missing
    }