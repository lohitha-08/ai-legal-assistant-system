import io
import os
import re
import sqlite3
from datetime import datetime
from functools import wraps
from io import BytesIO

import pandas as pd
from flask import (
    Flask,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    render_template_string,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename

from utils.complaint_draft_engine import generate_complaint_draft
from utils.evidence_engine import get_evidence_help
from utils.file_extractor import extract_text
from utils.ipc_engine import suggest_ipc as suggest_ipc_engine
from utils.lawyer_chatbot_engine import LAWYER_FEATURES, generate_lawyer_response
from utils.nlp_processor import (
    evidence_strength as analyze_evidence_strength,
    legal_risk,
    predict_ipc,
    punishment,
    summarize_case,
)
from utils.pdf_generator import generate_case_report
from flask import Flask, render_template, request
from utils.ask_law_engine import get_ask_law_answer
from utils.procedure_guide import get_procedure_answer
from utils.rights_helper import get_rights_answer
from utils.fir_guide_helper import get_fir_guide_answer
from utils.legal_faq_helper import get_faq_answer
from utils.ipc_finder_helper import get_ipc_finder_answer

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
DATA_FOLDER = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "database.db")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "legal_secret_key_dev")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB


# --------------------------------------------------
# DATABASE
# --------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            case_title TEXT NOT NULL,
            case_date TEXT NOT NULL,
            description TEXT NOT NULL,
            summary TEXT,
            predicted_ipc TEXT,
            evidence_strength TEXT,
            legal_risk TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            incident_type TEXT NOT NULL,
            incident_date TEXT NOT NULL,
            incident_location TEXT NOT NULL,
            description TEXT NOT NULL,
            ipc_section TEXT,
            status TEXT DEFAULT 'Complaint Received',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fir_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER,
            fir_text TEXT NOT NULL,
            ipc_section TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigation_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER,
            note_date TEXT NOT NULL,
            officer_name TEXT NOT NULL,
            note_text TEXT NOT NULL,
            next_action TEXT,
            status TEXT,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER,
            status TEXT,
            updated_date TEXT,
            remarks TEXT,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        )
    """)

    conn.commit()
    conn.close()


init_db()


# --------------------------------------------------
# AUTH HELPERS
# --------------------------------------------------
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "danger")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "danger")
                return redirect(url_for("login"))

            if session.get("role") != required_role:
                flash("Access denied.", "danger")
                return redirect(url_for("dashboard"))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


# --------------------------------------------------
# GENERAL HELPERS
# --------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_pdf(filename, title, lines):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title)
    y -= 30
    pdf.setFont("Helvetica", 11)

    for line in lines:
        text = str(line) if line is not None else ""
        split_lines = text.split("\n")

        for part in split_lines:
            while len(part) > 100:
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 11)
                    y = height - 50
                pdf.drawString(50, y, part[:100])
                part = part[100:]
                y -= 18

            if y < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y = height - 50

            pdf.drawString(50, y, part)
            y -= 18

    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def clean_text(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def suggest_ipc_local(incident_type, description=""):
    text = f"{incident_type} {description}".lower()

    if "theft" in text or "stolen" in text or "steal" in text:
        return "IPC 378 / 379 - Theft"
    if "assault" in text or "attack" in text or "hit" in text:
        return "IPC 351 / 352 - Assault"
    if "fraud" in text or "cheat" in text or "scam" in text:
        return "IPC 420 - Cheating and Fraud"
    if "threat" in text or "threaten" in text:
        return "IPC 506 - Criminal Intimidation"
    if "cyber" in text or "online" in text or "hack" in text:
        return "IT Act 66 / IPC 420 - Cyber Crime"
    if "murder" in text or "kill" in text:
        return "IPC 302 - Murder"
    if "kidnap" in text:
        return "IPC 363 - Kidnapping"

    return "IPC Section needs legal review"


def generate_evidence_list(case_text):
    text = (case_text or "").lower()

    if "theft" in text or "stolen" in text or "steal" in text:
        return [
            {"item": "Complainant statement", "strength": "High"},
            {"item": "Witness statements", "strength": "Medium"},
            {"item": "CCTV footage from location", "strength": "Very High"},
            {"item": "Photos of crime scene", "strength": "High"},
            {"item": "List of stolen items", "strength": "High"},
            {"item": "Ownership proof of stolen items", "strength": "Medium"},
            {"item": "Fingerprint evidence if available", "strength": "Very High"},
        ]

    if "assault" in text or "attack" in text or "hit" in text:
        return [
            {"item": "Victim statement", "strength": "High"},
            {"item": "Medical report / wound certificate", "strength": "Very High"},
            {"item": "Witness statements", "strength": "Medium"},
            {"item": "Weapon details if any", "strength": "High"},
            {"item": "Scene photographs", "strength": "Medium"},
            {"item": "CCTV footage", "strength": "Very High"},
            {"item": "Accused details", "strength": "Medium"},
        ]

    if "fraud" in text or "cheat" in text or "scam" in text:
        return [
            {"item": "Victim complaint statement", "strength": "High"},
            {"item": "Bank transaction records", "strength": "Very High"},
            {"item": "Call logs / chat screenshots", "strength": "High"},
            {"item": "Email or message proof", "strength": "High"},
            {"item": "Identity proof of accused if known", "strength": "Medium"},
            {"item": "Digital device evidence", "strength": "Very High"},
            {"item": "Related documents", "strength": "Medium"},
        ]

    if "cyber" in text or "online" in text or "hack" in text:
        return [
            {"item": "Screenshot of cyber incident", "strength": "Medium"},
            {"item": "Email/message headers", "strength": "High"},
            {"item": "Affected account details", "strength": "High"},
            {"item": "Device logs", "strength": "Very High"},
            {"item": "Bank transaction details if any", "strength": "High"},
            {"item": "IP / login history if available", "strength": "Very High"},
            {"item": "Digital forensic evidence", "strength": "Very High"},
        ]

    return [
        {"item": "Complainant statement", "strength": "High"},
        {"item": "Witness statements", "strength": "Medium"},
        {"item": "Scene photos", "strength": "Medium"},
        {"item": "Relevant documents", "strength": "High"},
        {"item": "CCTV footage if available", "strength": "High"},
        {"item": "Medical or forensic report if applicable", "strength": "Very High"},
    ]


# --------------------------------------------------
# IPC EXPLORER DATA
# --------------------------------------------------
IPC_FILE = os.path.join(DATA_FOLDER, "ipc_section_dataset.csv")

if os.path.exists(IPC_FILE):
    ipc_master_data = pd.read_csv(IPC_FILE)
else:
    ipc_master_data = pd.DataFrame([
        {
            "Section": "379",
            "Offense": "Theft",
            "Punishment": "Up to 3 years or fine or both",
            "Description": "Dishonestly taking movable property without consent.",
        },
        {
            "Section": "420",
            "Offense": "Cheating",
            "Punishment": "Up to 7 years and fine",
            "Description": "Cheating and dishonestly inducing delivery of property.",
        },
        {
            "Section": "351",
            "Offense": "Assault",
            "Punishment": "Punishment varies depending on facts",
            "Description": "Threat or use of criminal force.",
        },
        {
            "Section": "302",
            "Offense": "Murder",
            "Punishment": "Death or life imprisonment and fine",
            "Description": "Punishment for murder.",
        },
        {
            "Section": "506",
            "Offense": "Criminal Intimidation",
            "Punishment": "Imprisonment or fine or both",
            "Description": "Threatening a person with injury to body, reputation or property.",
        },
    ])

column_map = {
    "section": "Section",
    "title": "Offense",
    "offense": "Offense",
    "punishment": "Punishment",
    "explanation": "Description",
    "description": "Description",
}

ipc_master_data.columns = [
    column_map.get(str(c).strip().lower(), str(c).strip())
    for c in ipc_master_data.columns
]

for col in ["Section", "Offense", "Punishment", "Description"]:
    if col not in ipc_master_data.columns:
        ipc_master_data[col] = ""

ipc_master_data["Section"] = ipc_master_data["Section"].fillna("").astype(str)
ipc_master_data["Offense"] = ipc_master_data["Offense"].fillna("").astype(str)
ipc_master_data["Punishment"] = ipc_master_data["Punishment"].fillna("").astype(str)
ipc_master_data["Description"] = ipc_master_data["Description"].fillna("").astype(str)

ipc_master_data["combined"] = (
    ipc_master_data["Section"] + " "
    + ipc_master_data["Offense"] + " "
    + ipc_master_data["Punishment"] + " "
    + ipc_master_data["Description"]
).apply(clean_text)

# remove blank rows after cleaning
ipc_master_data = ipc_master_data[
    ipc_master_data["combined"].astype(str).str.strip() != ""
].copy()

# debug prints
print("IPC columns:", ipc_master_data.columns.tolist())
print("IPC row count after cleaning:", len(ipc_master_data))
print("IPC sample combined:", ipc_master_data["combined"].head(5).tolist())

# fallback if dataset becomes empty
if ipc_master_data.empty:
    ipc_master_data = pd.DataFrame([
        {
            "Section": "379",
            "Offense": "Theft",
            "Punishment": "Up to 3 years or fine or both",
            "Description": "Dishonestly taking movable property without consent."
        },
        {
            "Section": "420",
            "Offense": "Cheating",
            "Punishment": "Up to 7 years and fine",
            "Description": "Cheating and dishonestly inducing delivery of property."
        }
    ])

    ipc_master_data["combined"] = (
        ipc_master_data["Section"] + " "
        + ipc_master_data["Offense"] + " "
        + ipc_master_data["Punishment"] + " "
        + ipc_master_data["Description"]
    ).apply(clean_text)

vectorizer = TfidfVectorizer(stop_words="english")
ipc_vectors = vectorizer.fit_transform(ipc_master_data["combined"].tolist())


# --------------------------------------------------
# HOME
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("splash.html")


@app.route("/home")
def home_page():
    return render_template("home.html")


# --------------------------------------------------
# REGISTER
# --------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "").strip()

        if not username or not email or not password or not confirm_password or not role:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Password and Confirm Password do not match.", "danger")
            return redirect(url_for("register"))

        conn = get_db_connection()
        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username, email),
        ).fetchone()

        if existing_user:
            conn.close()
            flash("Username or Email already exists.", "danger")
            return redirect(url_for("login"))

        conn.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, password, role),
        )
        conn.commit()
        conn.close()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# --------------------------------------------------
# LOGIN / LOGOUT
# --------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role")

    if role == "Lawyer":
        return redirect(url_for("lawyer"))
    if role == "Police":
        return redirect(url_for("police"))
    if role == "Public":
        return redirect(url_for("public_page"))

    flash("Invalid role.", "danger")
    return redirect(url_for("login"))


# --------------------------------------------------
# LAWYER MODULE
# --------------------------------------------------
@app.route("/lawyer")
@role_required("Lawyer")
def lawyer():
    return render_template("lawyer.html")


@app.route("/case_upload", methods=["GET", "POST"])
@role_required("Lawyer")
def case_upload():
    if request.method == "POST":
        entry_mode = request.form.get("entry_mode", "manual")
        title = request.form.get("title", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()
        parties_involved = request.form.get("parties_involved", "").strip()
        case_file = request.files.get("file")

        text_parts = []

        if entry_mode == "upload":
            if not case_file or not case_file.filename:
                flash("Please upload a PDF or DOCX file.", "danger")
                return redirect(url_for("case_upload"))

            if not allowed_file(case_file.filename):
                flash("Only PDF and DOCX files are allowed.", "danger")
                return redirect(url_for("case_upload"))

            safe_filename = secure_filename(case_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], safe_filename)
            case_file.save(filepath)

            try:
                extracted = extract_text(filepath)
                if extracted:
                    text_parts.append(extracted)
            except Exception as e:
                flash(f"File processing error: {e}", "danger")
                return redirect(url_for("case_upload"))

            title = os.path.splitext(case_file.filename)[0]
            date = datetime.now().strftime("%Y-%m-%d")

        else:
            if not title or not date or not description:
                flash("Case title, case date and description are required.", "danger")
                return redirect(url_for("case_upload"))

            if parties_involved:
                text_parts.append(f"Parties Involved: {parties_involved}")
            text_parts.append(f"Case Description: {description}")

        full_text = "\n".join(text_parts).strip()

        if not full_text:
            flash("Please upload a file or enter case details.", "danger")
            return redirect(url_for("case_upload"))

        summary = summarize_case(full_text)
        ipc = predict_ipc(full_text)
        evidence = analyze_evidence_strength(full_text)
        risk = legal_risk(full_text)
        punish = punishment(ipc)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cases (
                user_id, case_title, case_date, description,
                summary, predicted_ipc, evidence_strength, legal_risk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"], title, date, full_text,
            summary, ipc, evidence, risk,
        ))
        case_id = cursor.lastrowid
        conn.commit()
        conn.close()

        safe_report_name = secure_filename(f"{title}_{case_id}.pdf")

        report_data = {
            "Case Title": title,
            "Date": date,
            "Predicted IPC": ipc,
            "Evidence Strength": evidence,
            "Punishment": punish,
            "Legal Risk": risk,
            "Summary": summary,
        }

        generate_case_report(report_data, safe_report_name)

        return render_template(
            "report_view.html",
            title=title,
            date=date,
            ipc=ipc,
            evidence=evidence,
            risk=risk,
            punishment=punish,
            summary=summary,
            report=safe_report_name,
        )

    return render_template("case_upload.html")


@app.route("/case_history")
@role_required("Lawyer")
def case_history():
    conn = get_db_connection()
    cases = conn.execute("""
        SELECT * FROM cases
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()
    conn.close()

    return render_template("case_history.html", cases=cases)


@app.route("/view_case/<int:case_id>")
@role_required("Lawyer")
def view_case(case_id):
    conn = get_db_connection()
    case = conn.execute("""
        SELECT * FROM cases
        WHERE id = ? AND user_id = ?
    """, (case_id, session["user_id"])).fetchone()
    conn.close()

    if not case:
        flash("Case not found.", "danger")
        return redirect(url_for("case_history"))

    report_filename = secure_filename(f"{case['case_title']}_{case['id']}.pdf")

    return render_template(
        "report_view.html",
        title=case["case_title"],
        date=case["case_date"],
        summary=case["summary"],
        ipc=case["predicted_ipc"],
        evidence=case["evidence_strength"],
        risk=case["legal_risk"],
        punishment="Refer generated report",
        report=report_filename,
    )


@app.route("/delete_case/<int:case_id>")
@role_required("Lawyer")
def delete_case(case_id):
    conn = get_db_connection()
    conn.execute("""
        DELETE FROM cases
        WHERE id = ? AND user_id = ?
    """, (case_id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Case deleted successfully.", "success")
    return redirect(url_for("case_history"))


@app.route("/analytics")
@role_required("Lawyer")
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT legal_risk, COUNT(*) AS count
            FROM cases
            WHERE legal_risk IS NOT NULL AND legal_risk != ''
              AND user_id = ?
            GROUP BY legal_risk
            ORDER BY count DESC
        """, (session["user_id"],))
        risk_data = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT predicted_ipc, COUNT(*) AS count
            FROM cases
            WHERE predicted_ipc IS NOT NULL AND predicted_ipc != ''
              AND user_id = ?
            GROUP BY predicted_ipc
            ORDER BY count DESC
            LIMIT 10
        """, (session["user_id"],))
        ipc_data = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT evidence_strength, COUNT(*) AS count
            FROM cases
            WHERE evidence_strength IS NOT NULL AND evidence_strength != ''
              AND user_id = ?
            GROUP BY evidence_strength
            ORDER BY count DESC
        """, (session["user_id"],))
        evidence_data = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT substr(case_date, 6, 2) AS month, COUNT(*) AS count
            FROM cases
            WHERE case_date IS NOT NULL AND case_date != ''
              AND user_id = ?
            GROUP BY substr(case_date, 6, 2)
            ORDER BY month
        """, (session["user_id"],))
        monthly_data = [dict(row) for row in cursor.fetchall()]

    except Exception as e:
        print("Analytics error:", e)
        risk_data = []
        ipc_data = []
        evidence_data = []
        monthly_data = []
    finally:
        conn.close()

    return render_template(
        "analytics.html",
        risk_data=risk_data,
        ipc_data=ipc_data,
        evidence_data=evidence_data,
        monthly_data=monthly_data,
    )


@app.route("/lawyer_chatbot")
@role_required("Lawyer")
def lawyer_chatbot():
    return render_template("lawyer_chatbot.html", features=LAWYER_FEATURES)


@app.route("/chatbot_response", methods=["POST"])
@role_required("Lawyer")
def chatbot_response():
    user_message = request.form.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter your legal question."})

    bot_reply = generate_lawyer_response(user_message)
    return jsonify({"response": bot_reply})


@app.route("/download_report/<path:filename>")
@login_required
def download_report(filename):
    return send_from_directory(
        app.config["REPORT_FOLDER"],
        filename,
        as_attachment=True,
    )


# --------------------------------------------------
# POLICE MODULE
# --------------------------------------------------
@app.route("/police")
@role_required("Police")
def police():
    return render_template("police.html")

@app.route("/complaint_entry", methods=["GET", "POST"])
@role_required("Police")
def complaint_entry():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        incident_type = request.form.get("incident_type", "").strip() or request.form.get("offence", "").strip()
        incident_date = request.form.get("incident_date", "").strip() or request.form.get("date", "").strip()
        incident_location = request.form.get("incident_location", "").strip() or request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()

        if not name or not phone or not incident_type or not incident_date or not incident_location or not description:
            flash("Please fill all required complaint details.", "danger")
            return redirect(url_for("complaint_entry"))

        ipc_section = suggest_ipc_local(incident_type, description)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaints (
                name, phone, address, incident_type, incident_date,
                incident_location, description, ipc_section
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, phone, address, incident_type, incident_date,
            incident_location, description, ipc_section,
        ))
        complaint_id = cursor.lastrowid
        conn.commit()
        conn.close()

        complaint = {
            "id": complaint_id,
            "name": name,
            "phone": phone,
            "address": address,
            "date": incident_date,
            "location": incident_location,
            "offence": incident_type,
            "description": description,
            "ipc_section": ipc_section,
        }
        return render_template("complaint_result.html", complaint=complaint)

    return render_template("complaint_entry.html")




@app.route("/view_complaints")
@role_required("Police")
def view_complaints():
    conn = get_db_connection()
    complaints = conn.execute("""
        SELECT * FROM complaints
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    template_path = os.path.join(BASE_DIR, "templates", "view_complaints.html")
    if os.path.exists(template_path):
        return render_template("view_complaints.html", complaints=complaints)

    return render_template_string("""
    <html>
    <head>
        <title>View Complaints</title>
        <style>
            body{font-family:Arial;background:#f5f5f5;padding:30px}
            table{width:100%;border-collapse:collapse;background:white}
            th,td{border:1px solid #ddd;padding:10px;text-align:left}
            th{background:#222;color:white}
            a{color:#2563eb;text-decoration:none}
        </style>
    </head>
    <body>
        <h2>Complaints</h2>
        <table>
            <tr>
                <th>ID</th><th>Name</th><th>Phone</th><th>Incident</th><th>Location</th><th>Status</th>
            </tr>
            {% for c in complaints %}
            <tr>
                <td>{{ c.id }}</td>
                <td>{{ c.name }}</td>
                <td>{{ c.phone }}</td>
                <td>{{ c.incident_type }}</td>
                <td>{{ c.incident_location }}</td>
                <td>{{ c.status }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, complaints=complaints)


@app.route("/download_complaint/<int:complaint_id>")
@role_required("Police")
def download_complaint(complaint_id):
    conn = get_db_connection()
    complaint = conn.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
    conn.close()

    if not complaint:
        flash("Complaint not found.", "danger")
        return redirect(url_for("view_complaints"))

    return build_pdf(
        filename=f"complaint_{complaint_id}.pdf",
        title="Complaint Record",
        lines=[
            f"Complaint ID: {complaint['id']}",
            f"Name: {complaint['name']}",
            f"Phone: {complaint['phone']}",
            f"Address: {complaint['address']}",
            f"Incident Type: {complaint['incident_type']}",
            f"Incident Date: {complaint['incident_date']}",
            f"Incident Location: {complaint['incident_location']}",
            f"IPC Section: {complaint['ipc_section']}",
            f"Status: {complaint['status']}",
            "",
            "Description:",
            complaint["description"],
        ],
    )


@app.route("/delete_complaint/<int:complaint_id>")
@role_required("Police")
def delete_complaint(complaint_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()

    flash("Complaint deleted successfully.", "success")
    return redirect(url_for("view_complaints"))


@app.route("/fir_generator", methods=["GET", "POST"])
@role_required("Police")
def fir_generator():
    if request.method == "POST":
        complaint_id = request.form.get("complaint_id", "").strip()
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        incident_date = request.form.get("incident_date", "").strip()
        incident_time = request.form.get("incident_time", "").strip()
        time_format = request.form.get("time_format", "").strip()
        location = request.form.get("location", "").strip()
        accused = request.form.get("accused", "").strip()
        evidence = request.form.get("evidence", "").strip()
        witness = request.form.get("witness", "").strip()
        description = request.form.get("description", "").strip()

        full_time = f"{incident_time} {time_format}".strip()

        fir_text = f"""
FIR Draft

Name: {name}
Phone: {phone}
Address: {address}

Incident Date: {incident_date}
Incident Time: {full_time}
Location: {location}

Accused (if known): {accused}
Evidence: {evidence}
Witness: {witness}

Complaint Description:
{description}
        """.strip()

        ipc_section = suggest_ipc_local("", description)

        if complaint_id.isdigit():
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO fir_reports (complaint_id, fir_text, ipc_section)
                VALUES (?, ?, ?)
            """, (int(complaint_id), fir_text, ipc_section))
            conn.execute("""
                UPDATE complaints
                SET status = 'FIR Generated'
                WHERE id = ?
            """, (int(complaint_id),))
            conn.commit()
            conn.close()

        return render_template(
            "fir_result.html",
            fir=fir_text,
            name=name,
            phone=phone,
            address=address,
            incident_date=incident_date,
            incident_time=full_time,
            location=location,
            accused=accused,
            evidence=evidence,
            witness=witness,
            description=description,
        )

    conn = get_db_connection()
    complaints = conn.execute("""
        SELECT id, name, incident_type, incident_date, incident_location
        FROM complaints
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    return render_template("fir_generator.html", complaints=complaints)


@app.route("/download_fir", methods=["POST"])
@role_required("Police")
def download_fir():
    fir = request.form.get("fir", "")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    y = 800

    for line in fir.split("\n"):
        p.drawString(60, y, line.strip()[:110])
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="FIR.pdf",
        mimetype="application/pdf",
    )


@app.route("/ipc_suggestion", methods=["GET", "POST"])
@role_required("Police")
def ipc_suggestion():
    if request.method == "POST":
        case_text = request.form.get("case_text", "")
        result = suggest_ipc_engine(case_text)
        return render_template("ipc_result.html", case_text=case_text, result=result)

    return render_template("ipc_suggestion.html")


@app.route("/download_ipc_pdf", methods=["POST"])
@role_required("Police")
def download_ipc_pdf():
    case_text = request.form.get("case_text", "")
    result = request.form.get("result", "")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    y = 800

    lines = [
        "IPC Suggestion Report",
        "",
        "Case Details:",
        case_text,
        "",
        "Suggested IPC:",
        result,
    ]

    for block in lines:
        for line in str(block).split("\n"):
            p.drawString(50, y, line[:100])
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="IPC_Report.pdf",
        mimetype="application/pdf",
    )


@app.route("/evidence_strength", methods=["GET", "POST"])
@role_required("Police")
def evidence_strength_page():
    if request.method == "POST":
        evidence_weights = {
            "witness": 15,
            "victim_statement": 10,
            "video": 20,
            "photo": 10,
            "document": 10,
            "audio": 8,
            "cctv": 18,
            "mobile_data": 12,
            "forensic": 20,
            "fingerprint": 18,
            "medical": 15,
            "weapon": 12,
            "location": 8,
            "confession": 14,
            "digital": 15,
            "seizure": 10,
        }

        selected = []
        score = 0

        for key, weight in evidence_weights.items():
            if request.form.get(key):
                selected.append(key)
                score += weight

        score = min(int(score), 100)

        if score >= 75:
            result = "Strong Evidence"
            verdict = "Case appears well-supported with strong available evidence."
        elif score >= 45:
            result = "Moderate Evidence"
            verdict = "Case has partial support, but stronger corroborative evidence is needed."
        else:
            result = "Weak Evidence"
            verdict = "Case currently lacks enough strong supporting evidence."

        breakdown = [{"name": key.replace("_", " ").title(), "points": evidence_weights[key]} for key in selected]

        weak_points = []
        if "witness" not in selected:
            weak_points.append("No witness statement")
        if "video" not in selected and "cctv" not in selected:
            weak_points.append("No video or CCTV evidence")
        if "forensic" not in selected and "fingerprint" not in selected:
            weak_points.append("No forensic or fingerprint support")
        if "document" not in selected and "digital" not in selected:
            weak_points.append("No documentary or digital proof")

        suggestions = []
        if "witness" not in selected:
            suggestions.append("Collect witness statements.")
        if "cctv" not in selected:
            suggestions.append("Check nearby CCTV footage.")
        if "forensic" not in selected:
            suggestions.append("Request forensic examination if relevant.")
        if "medical" not in selected:
            suggestions.append("Add medical report where applicable.")
        if "mobile_data" not in selected:
            suggestions.append("Verify mobile call or chat records.")

        return render_template(
            "evidence_result.html",
            score=score,
            result=result,
            verdict=verdict,
            breakdown=breakdown,
            weak_points=weak_points,
            suggestions=suggestions,
        )

    return render_template("evidence_checklist.html")

notes = []

@app.route("/investigation_notes", methods=["GET", "POST"])
def investigation_notes():
    if request.method == "POST":
        title = request.form.get("title", "")
        details = request.form.get("details", "")

        note = {
            "title": title,
            "details": details,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        notes.append(note)

    return render_template("investigation_notes.html", notes=notes)


@app.route("/delete_note/<int:index>")
def delete_note(index):
    if 0 <= index < len(notes):
        notes.pop(index)
    return redirect(url_for("investigation_notes"))


@app.route("/case_status")
def case_status():
    selected_status = request.args.get("status", "All Statuses")

    cases_data = [
        {
            "fir_no": "FIR-101",
            "case_title": "Mobile Theft Complaint",
            "date": "26-03-2026",
            "status": "Investigation"
        },
        {
            "fir_no": "FIR-102",
            "case_title": "Online Fraud Report",
            "date": "25-03-2026",
            "status": "Charge Sheet Filed"
        },
        {
            "fir_no": "FIR-103",
            "case_title": "Assault Case",
            "date": "24-03-2026",
            "status": "Under Review"
        },
        {
            "fir_no": "FIR-104",
            "case_title": "Chain Snatching Case",
            "date": "23-03-2026",
            "status": "Closed"
        }
    ]

    if selected_status == "All Statuses":
        filtered_cases = cases_data
    else:
        filtered_cases = [
            case for case in cases_data
            if case["status"] == selected_status
        ]

    return render_template(
        "case_status.html",
        cases=filtered_cases,
        selected_status=selected_status
    )

# -------------------------
# PUBLIC MODULE ROUTES
# -------------------------

@app.route("/public_page")
def public_page():
    return render_template("public.html")


# 1. AI Legal Assistant
@app.route("/ask_law", methods=["GET", "POST"])
def ask_law():
    if request.method == "POST":
        question = request.form.get("question", "").strip()

        if not question:
            return render_template(
                "ask_law.html",
                error="Please enter your legal question."
            )

        result = get_ask_law_answer(question)

        return render_template(
            "ask_law_result.html",
            question=question,
            result=result
        )

    return render_template("ask_law.html")


# 2. Step-by-Step Guide
@app.route("/procedure_guide", methods=["GET", "POST"])
def procedure_guide():
    if request.method == "POST":
        situation = request.form.get("situation", "").strip()

        if not situation:
            return render_template(
                "procedure_guide.html",
                error="Please enter your situation."
            )

        result = get_procedure_answer(situation)

        return render_template(
            "procedure_result.html",
            situation=situation,
            result=result
        )

    return render_template("procedure_guide.html")

# 3. Rights Awareness
@app.route("/rights_awareness", methods=["GET", "POST"])
def rights_awareness():
    if request.method == "POST":
        user_query = request.form.get("query", "").strip()

        if not user_query:
            return render_template(
                "rights_awareness.html",
                error="Please enter your question."
            )

        result = get_rights_answer(user_query)

        print("USER QUERY:", user_query)
        print("RESULT:", result)

        return render_template(
            "rights_result.html",
            user_query=user_query,
            result=result
        )

    return render_template("rights_awareness.html")

# 4. FIR Info Guide
@app.route("/fir_guide", methods=["GET", "POST"])
def fir_guide():

    if request.method == "POST":
        user_query = request.form.get("query")

        print("QUERY =", user_query)   # debug

        if not user_query:
            return render_template("fir_guide.html", error="Enter question")

        result = get_fir_guide_answer(user_query)

        print("RESULT =", result)   # debug

        # ✅ IMPORTANT: result page render panna vendum
        return render_template(
            "fir_guide_result.html",
            user_query=user_query,
            result=result
        )

    return render_template("fir_guide.html")


# 5. Legal FAQ
@app.route("/legal_faq", methods=["GET", "POST"])
def legal_faq():
    if request.method == "POST":
        user_query = request.form.get("query", "").strip()

        print("QUERY =", user_query)

        if not user_query:
            return render_template(
                "legal_faq.html",
                error="Please enter your legal question."
            )

        result = get_faq_answer(user_query)

        print("RESULT =", result)

        return render_template(
            "legal_faq_result.html",
            user_query=user_query,
            result=result
        )

    return render_template("legal_faq.html")


# 6. IPC / BNS Section Finder
@app.route("/ipc_finder", methods=["GET", "POST"])
def ipc_finder():
    if request.method == "POST":
        user_query = request.form.get("query", "").strip()

        print("QUERY =", user_query)

        if not user_query:
            return render_template(
                "ipc_finder.html",
                error="Please describe the issue."
            )

        result = get_ipc_finder_answer(user_query)

        print("RESULT =", result)

        return render_template(
            "ipc_finder_result.html",
            user_query=user_query,
            result=result
        )

    return render_template("ipc_finder.html")



# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------
@app.errorhandler(404)
def not_found_error(_error):
    return render_template_string("""
    <html>
    <head><title>404</title></head>
    <body style="font-family:Arial;padding:40px">
        <h2>404 - Page not found</h2>
        <p>The page you are looking for does not exist.</p>
        <a href="/home">Go to Home</a>
    </body>
    </html>
    """), 404


@app.errorhandler(413)
def file_too_large(_error):
    flash("Uploaded file is too large.", "danger")
    return redirect(request.referrer or url_for("home_page"))


@app.errorhandler(500)
def internal_server_error(_error):
    return render_template_string("""
    <html>
    <head><title>500</title></head>
    <body style="font-family:Arial;padding:40px">
        <h2>500 - Internal Server Error</h2>
        <p>Something went wrong in the application.</p>
        <a href="/home">Go to Home</a>
    </body>
    </html>
    """), 500


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)