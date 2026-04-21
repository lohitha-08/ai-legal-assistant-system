from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


def generate_case_report(data, filename):

    path = os.path.join("reports", filename)

    c = canvas.Canvas(path, pagesize=letter)

    y = 750

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y, "AI Legal Case Report")

    y -= 40

    c.setFont("Helvetica", 12)

    for key, value in data.items():

        line = f"{key}: {value}"

        c.drawString(100, y, line)

        y -= 25

    c.save()

    return path