import os
import re
import pandas as pd

# -----------------------------
# PATH SETUP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "ipc_section_dataset.csv")

# -----------------------------
# CHATBOT FEATURES LIST
# -----------------------------
LAWYER_FEATURES = [
    "1. Legal Term Explanation",
    "2. IPC / BNS Section Explanation",
    "3. Punishment Information",
    "4. Bail Information",
    "5. Section Predictor",
    "6. Case Summary Explain",
    "7. Evidence Guidance",
    "8. Case Type Identifier",
    "9. Legal Rights Guide",
    "10. Court Process Guide",
    "11. Legal Document Explanation",
    "12. Legal Notice Generator",
    "13. Case Law Explanation",
    "14. Case Outcome Explanation",
    "15. Lawyer Recommendation",
    "16. Document Checklist",
    "17. Legal Deadline Info",
    "18. Court Types Explanation",
    "19. Crime Category Explanation",
    "20. Legal Procedure Guide",
    "21. Legal Advice Tips",
    "22. Legal FAQ System",
    "23. Case Duration Estimate",
    "24. Settlement / Mediation Guidance",
    "25. Jurisdiction Guide",
    "26. Compoundable / Non-Compoundable Info",
    "27. General Lawyer Chat Support"
]

# -----------------------------
# LEGAL TERMS
# -----------------------------
LEGAL_TERMS = {
    "bail": "Bail means temporary release of an accused person from custody until the case is decided.",
    "fir": "FIR means First Information Report. It is the first complaint registered by police.",
    "charge sheet": "Charge sheet is the final police report submitted to court after investigation.",
    "warrant": "A warrant is a court order authorizing police to arrest or search.",
    "summons": "Summons is a court order asking a person to appear before court.",
    "affidavit": "An affidavit is a sworn written statement used as evidence.",
    "injunction": "An injunction is a court order directing a person to do or stop doing a specific act.",
    "appeal": "Appeal means asking a higher court to review the lower court decision."
}

# -----------------------------
# RIGHTS GUIDE
# -----------------------------
RIGHTS_GUIDE = {
    "arrest": [
        "Right to know grounds of arrest",
        "Right to inform family or friend",
        "Right to consult a lawyer",
        "Must be produced before magistrate within 24 hours in most cases"
    ],
    "women": [
        "Right against harassment",
        "Right to file complaint",
        "Right to privacy during investigation",
        "Right to legal protection in applicable cases"
    ],
    "consumer": [
        "Right to safety",
        "Right to information",
        "Right to choose",
        "Right to seek redressal"
    ]
}

# -----------------------------
# FAQ SYSTEM
# -----------------------------
FAQS = {
    "what is bail": "Bail is temporary release from custody until trial.",
    "what is fir": "FIR is the first complaint registered by police.",
    "what is charge sheet": "Charge sheet is the police investigation report submitted to court.",
    "what is anticipatory bail": "Anticipatory bail is pre-arrest bail granted by a court."
}

# -----------------------------
# TEXT NORMALIZATION
# -----------------------------
def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

# -----------------------------
# DATASET LOADERS
# -----------------------------
def load_normal_csv(file_path: str):
    try:
        df = pd.read_csv(file_path, encoding="latin1")
        df.columns = df.columns.str.strip().str.lower()

        required = {"section", "title", "punishment"}
        if not required.issubset(set(df.columns)):
            return None

        section_info = {}

        for _, row in df.iterrows():
            section = str(row.get("section", "")).strip().lower()
            if not section or section == "nan":
                continue

            section_info[section] = {
                "title": str(row.get("title", "")).strip(),
                "explanation": str(row.get("explanation", "")).strip() if "explanation" in df.columns else "",
                "punishment": str(row.get("punishment", "")).strip(),
            }

        return section_info
    except Exception:
        return None


def load_malformed_ipc_text(file_path: str):
    try:
        with open(file_path, "r", encoding="latin1") as f:
            raw = f.read()

        lines = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            line = line.replace('""', '"')
            lines.append(line)

        cleaned = "\n".join(lines)

        block_pattern = re.compile(
            r'"?(IPC|BNS)\s*([0-9]+[A-Z]?)"?\s*:\s*\{(.*?)\}',
            re.IGNORECASE | re.DOTALL
        )

        title_pattern = re.compile(r'"title"\s*:\s*"([^"]*)"', re.IGNORECASE)
        explanation_pattern = re.compile(r'"explanation"\s*:\s*"([^"]*)"', re.IGNORECASE)
        punishment_pattern = re.compile(r'"punishment"\s*:\s*"([^"]*)"', re.IGNORECASE)

        section_info = {}

        for match in block_pattern.finditer(cleaned):
            law_type = match.group(1).lower()
            sec_no = match.group(2).lower()
            body = match.group(3)

            key = f"{law_type} {sec_no}"

            title_match = title_pattern.search(body)
            explanation_match = explanation_pattern.search(body)
            punishment_match = punishment_pattern.search(body)

            title = title_match.group(1).strip() if title_match else ""
            explanation = explanation_match.group(1).strip() if explanation_match else ""
            punishment = punishment_match.group(1).strip() if punishment_match else ""

            if not explanation:
                if title:
                    explanation = f"This section deals with {title.lower()}."
                else:
                    explanation = "Explanation not available."

            section_info[key] = {
                "title": title if title else f"Section {sec_no}",
                "explanation": explanation,
                "punishment": punishment if punishment else "Punishment information not available."
            }

        return section_info
    except Exception:
        return {}


def load_section_info(file_path: str):
    if not os.path.exists(file_path):
        print(f"[WARNING] Dataset file not found: {file_path}")
        return {}

    csv_data = load_normal_csv(file_path)
    if csv_data:
        print(f"[INFO] Loaded {len(csv_data)} sections from normal CSV format.")
        return csv_data

    text_data = load_malformed_ipc_text(file_path)
    if text_data:
        print(f"[INFO] Loaded {len(text_data)} sections from malformed text format.")
        return text_data

    print("[WARNING] Could not parse IPC/BNS dataset.")
    return {}


SECTION_INFO = load_section_info(CSV_PATH)

# -----------------------------
# FIND IPC / BNS SECTION
# -----------------------------
def find_section(query: str):
    query = normalize_text(query)

    for key, value in SECTION_INFO.items():
        if key in query:
            return key, value

    ipc_match = re.search(r"(?:ipc\s*)?(\d+[a-z]?)", query, re.IGNORECASE)
    bns_match = re.search(r"(?:bns\s*)(\d+[a-z]?)", query, re.IGNORECASE)

    if bns_match:
        sec = f"bns {bns_match.group(1).lower()}"
        if sec in SECTION_INFO:
            return sec, SECTION_INFO[sec]

    if ipc_match:
        sec = f"ipc {ipc_match.group(1).lower()}"
        if sec in SECTION_INFO:
            return sec, SECTION_INFO[sec]

    return None, None

# -----------------------------
# HANDLERS
# -----------------------------
def explain_legal_term(query):
    q = normalize_text(query)
    for term, meaning in LEGAL_TERMS.items():
        if term in q:
            return f"**Legal Term: {term.title()}**\n\n{meaning}"
    return ""


def explain_section(query):
    sec_key, sec_data = find_section(query)
    if sec_data:
        return (
            f"**Section: {sec_key.upper()}**\n\n"
            f"**Title:** {sec_data['title']}\n"
            f"**Explanation:** {sec_data['explanation']}\n"
            f"**Punishment:** {sec_data['punishment']}"
        )
    return ""


def punishment_info(query):
    sec_key, sec_data = find_section(query)
    if sec_data:
        return f"**Punishment for {sec_key.upper()}**\n\n{sec_data['punishment']}"

    q = normalize_text(query)
    if "theft" in q:
        return "**Punishment Info:** Theft may lead to imprisonment, fine, or both depending on facts and section."
    if "cheating" in q or "fraud" in q:
        return "**Punishment Info:** Cheating-related offences may involve imprisonment and fine depending on the section."
    return ""


def bail_information(query):
    q = normalize_text(query)

    if "anticipatory bail" in q:
        return (
            "**Anticipatory Bail**\n\n"
            "Anticipatory bail is pre-arrest bail. A person fearing arrest may apply before the appropriate court."
        )

    if "regular bail" in q:
        return (
            "**Regular Bail**\n\n"
            "Regular bail is sought after arrest for release from custody."
        )

    if "bail" in q:
        return (
            "**Bail Information**\n\n"
            "Bail means temporary release from custody.\n\n"
            "- In bailable offences, bail is generally available as a matter of right.\n"
            "- In non-bailable offences, bail depends on court discretion.\n"
            "- Court may consider seriousness, evidence, and risk factors."
        )
    return ""


def section_predictor(query):
    q = normalize_text(query)

    if any(word in q for word in ["cheat", "fraud", "scam", "money taken"]):
        return "**Possible Section Prediction:** This may involve cheating-related provisions such as IPC 420."
    if any(word in q for word in ["theft", "stolen", "stole", "took my bike"]):
        return "**Possible Section Prediction:** This may involve theft-related provisions such as IPC 379."
    if any(word in q for word in ["hit me", "assault", "hurt", "injury"]):
        return "**Possible Section Prediction:** This may involve hurt / assault-related sections such as IPC 323."
    return ""


def case_summary_explain(query):
    q = normalize_text(query)
    if "summary" in q or "summarize" in q or "case summary" in q:
        return (
            "**Case Summary Help**\n\n"
            "A proper case summary should include:\n"
            "1. Parties involved\n"
            "2. Facts of the case\n"
            "3. Date/time of incident\n"
            "4. Evidence available\n"
            "5. Relevant legal sections\n"
            "6. Current case stage\n"
            "7. Relief requested"
        )
    return ""


def evidence_guidance(query):
    q = normalize_text(query)
    if "evidence" in q or "proof" in q:
        strength = "Moderate"

        if any(x in q for x in ["cctv", "video", "signed document", "medical report"]):
            strength = "Strong"
        elif any(x in q for x in ["whatsapp", "chat", "call recording", "screenshot"]):
            strength = "Moderate to Strong"
        elif any(x in q for x in ["only witness", "no proof", "doubt"]):
            strength = "Weak to Moderate"

        return (
            "**Evidence Guidance**\n\n"
            "Common evidence types:\n"
            "- Documents\n"
            "- CCTV / Photos / Videos\n"
            "- Medical reports\n"
            "- Witness statements\n"
            "- Audio / Chats / Emails\n\n"
            f"**Estimated Evidence Strength:** {strength}"
        )
    return ""


def case_type_identifier(query):
    q = normalize_text(query)

    if any(x in q for x in ["divorce", "maintenance", "child custody"]):
        return "**Case Type:** Family Law matter."
    if any(x in q for x in ["cheating", "theft", "assault", "threat", "fraud"]):
        return "**Case Type:** Criminal Law matter."
    if any(x in q for x in ["agreement", "money recovery", "contract", "property dispute"]):
        return "**Case Type:** Civil Law matter."
    if any(x in q for x in ["termination", "salary", "workplace harassment"]):
        return "**Case Type:** Labour / Employment matter."
    return ""


def legal_rights_guide(query):
    q = normalize_text(query)

    for category, items in RIGHTS_GUIDE.items():
        if category in q:
            text = "\n".join(f"- {i}" for i in items)
            return f"**Legal Rights ({category.title()})**\n\n{text}"

    if "rights" in q:
        return "**Legal Rights Guide:** Please mention the situation like arrest, women, consumer, property, or employment."
    return ""


def court_process_guide(query):
    q = normalize_text(query)
    if "court process" in q or "how court works" in q or "trial process" in q:
        return (
            "**Court Process Guide**\n\n"
            "1. Complaint / FIR\n"
            "2. Investigation\n"
            "3. Charge sheet / plaint filing\n"
            "4. Court takes cognizance\n"
            "5. Notice / summons\n"
            "6. Hearing / evidence stage\n"
            "7. Arguments\n"
            "8. Judgment\n"
            "9. Appeal if needed"
        )
    return ""


def legal_document_explanation(query):
    q = normalize_text(query)
    if "notice" in q and "explain" in q:
        return "**Legal Document Explanation:** A legal notice is a formal written communication sent before legal proceedings."
    if "affidavit" in q:
        return "**Legal Document Explanation:** An affidavit is a sworn written statement used as evidence."
    if "agreement" in q:
        return "**Legal Document Explanation:** An agreement records terms accepted between parties."
    if "document explanation" in q:
        return "**Legal Document Explanation:** Mention document name such as FIR, charge sheet, affidavit, agreement, sale deed, will, or legal notice."
    return ""


def legal_notice_generator(query):
    q = normalize_text(query)
    if "legal notice" in q or "notice draft" in q or "generate notice" in q:
        return (
            "**Basic Legal Notice Format**\n\n"
            "From:\nYour Name\nAddress\n\n"
            "To:\nRecipient Name\nAddress\n\n"
            "Subject: Legal Notice regarding [issue]\n\n"
            "Sir/Madam,\n"
            "Under instructions from my client, I hereby call upon you to [state grievance]. "
            "You are requested to comply within [X] days, failing which legal action may be initiated.\n\n"
            "Date:\nPlace:\nSignature"
        )
    return ""


def case_law_explanation(query):
    q = normalize_text(query)
    if "case law" in q or "judgment" in q or "precedent" in q:
        return "**Case Law Explanation**\n\nCase law means previous court judgments used as guidance in similar matters."
    return ""


def case_outcome_explanation(query):
    q = normalize_text(query)
    if "outcome" in q or "what will happen" in q or "result of case" in q:
        return "**Case Outcome Explanation**\n\nPossible outcomes include dismissal, acquittal, conviction, settlement, compensation, injunction, decree, or appeal."
    return ""


def lawyer_recommendation(query):
    q = normalize_text(query)
    if "lawyer recommendation" in q or "which lawyer" in q or "need lawyer" in q:
        return (
            "**Lawyer Recommendation Guide**\n\n"
            "- Criminal case → Criminal lawyer\n"
            "- Divorce / family → Family lawyer\n"
            "- Property dispute → Civil / property lawyer\n"
            "- Company issue → Corporate lawyer\n"
            "- Labour issue → Labour lawyer"
        )
    return ""


def document_checklist(query):
    q = normalize_text(query)
    if "document checklist" in q or "what documents needed" in q or "documents" in q:
        return (
            "**Legal Document Checklist**\n\n"
            "- ID proof\n"
            "- Address proof\n"
            "- FIR copy / complaint copy\n"
            "- Supporting documents\n"
            "- Photos / screenshots / recordings\n"
            "- Medical records if any\n"
            "- Witness details"
        )
    return ""


def legal_deadline_info(query):
    q = normalize_text(query)
    if "deadline" in q or "limitation" in q or "last date" in q:
        return "**Legal Deadline Info**\n\nDeadlines depend on case type, court, and law involved. Exact calculation should be checked based on dates and forum."
    return ""


def court_types_explanation(query):
    q = normalize_text(query)
    if "court types" in q or "which court" in q:
        return (
            "**Court Types**\n\n"
            "- Magistrate Court\n"
            "- Sessions Court\n"
            "- Civil Court\n"
            "- Family Court\n"
            "- Consumer Court / Commission\n"
            "- Labour Court\n"
            "- High Court\n"
            "- Supreme Court"
        )
    return ""


def crime_category_explanation(query):
    q = normalize_text(query)
    if "crime category" in q or "type of crime" in q:
        return (
            "**Crime Categories**\n\n"
            "- Property offences\n"
            "- Violent offences\n"
            "- Financial offences\n"
            "- Cyber offences\n"
            "- Sexual offences\n"
            "- Public order offences"
        )
    return ""


def legal_procedure_guide(query):
    q = normalize_text(query)
    if "procedure" in q or "legal procedure" in q:
        return "**Legal Procedure Guide**\n\nBasic procedure includes complaint, document collection, filing, notice stage, hearing, evidence, and final order."
    return ""


def legal_advice_tips(query):
    q = normalize_text(query)
    if "advice" in q or "what should i do" in q:
        return (
            "**Legal Advice Tips**\n\n"
            "- Keep documents safely\n"
            "- Preserve evidence\n"
            "- Note dates clearly\n"
            "- Do not sign without reading\n"
            "- Consult a qualified lawyer for final legal action"
        )
    return ""


def legal_faq_system(query):
    q = normalize_text(query)
    for question, answer in FAQS.items():
        if question in q:
            return f"**FAQ Answer**\n\n{answer}"

    if "faq" in q:
        return "**FAQ Topics:** You can ask about bail, FIR, arrest, charge sheet, legal notice, anticipatory bail, and court process."
    return ""


def case_duration_estimate(query):
    q = normalize_text(query)
    if "how long" in q or "duration" in q or "time for case" in q:
        return "**Case Duration Estimate**\n\nDuration depends on case type, court workload, evidence, witness attendance, interim applications, and appeals."
    return ""


def mediation_guidance(query):
    q = normalize_text(query)
    if "mediation" in q or "settlement" in q or "compromise" in q:
        return "**Settlement / Mediation Guidance**\n\nMediation is a voluntary process where parties try to resolve the dispute peacefully with the help of a neutral mediator."
    return ""


def jurisdiction_guide(query):
    q = normalize_text(query)
    if "where to file" in q or "jurisdiction" in q:
        return "**Jurisdiction Guide**\n\nJurisdiction may depend on place of cause of action, place of offence, residence of parties, and subject matter."
    return ""


def compoundable_info(query):
    q = normalize_text(query)
    if "compoundable" in q or "non-compoundable" in q:
        return "**Compoundable / Non-Compoundable Offence Info**\n\nCompoundable offences may be settled between parties where law allows. Non-compoundable offences generally proceed under criminal law."
    return ""


def general_help_response():
    return (
        "**Lawyer Chatbot Help**\n\n"
        "You can ask:\n"
        "- Explain bail\n"
        "- Explain IPC 420\n"
        "- What punishment for theft?\n"
        "- Predict section for cheating case\n"
        "- Explain court process\n"
        "- What documents are needed?\n"
        "- What rights do I have after arrest?"
    )

# -----------------------------
# MAIN CHATBOT FUNCTION
# -----------------------------
def generate_lawyer_response(user_query):
    query = normalize_text(user_query)

    handlers = [
        explain_legal_term,
        explain_section,
        punishment_info,
        bail_information,
        section_predictor,
        case_summary_explain,
        evidence_guidance,
        case_type_identifier,
        legal_rights_guide,
        court_process_guide,
        legal_document_explanation,
        legal_notice_generator,
        case_law_explanation,
        case_outcome_explanation,
        lawyer_recommendation,
        document_checklist,
        legal_deadline_info,
        court_types_explanation,
        crime_category_explanation,
        legal_procedure_guide,
        legal_advice_tips,
        legal_faq_system,
        case_duration_estimate,
        mediation_guidance,
        jurisdiction_guide,
        compoundable_info
    ]

    for handler in handlers:
        result = handler(query)
        if result:
            return result

    return general_help_response()