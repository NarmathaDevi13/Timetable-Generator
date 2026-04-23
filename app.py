from flask import Flask, render_template, request, send_file
from generator import Subject, TimeTable
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
import io

app = Flask(__name__)

generated_table = []
department = ""
semester = ""
section = ""


@app.route("/", methods=["GET", "POST"])
def home():
    global generated_table, department, semester, section

    if request.method == "POST":
        department = request.form.get("department")
        semester = request.form.get("semester")
        section = request.form.get("section")

        n = int(request.form.get("n"))

        subjects = []

        for i in range(n):
            name = request.form.get(f"name{i}")
            hours = int(request.form.get(f"hours{i}") or 0)
            credit = int(request.form.get(f"credit{i}") or 0)
            type_ = request.form.get(f"type{i}")
            lab = int(request.form.get(f"lab{i}") or 0)

            subjects.append(Subject(name, hours, credit, type_, lab))

        tt = TimeTable()
        tt.allocate_lab(subjects)
        tt.allocate_theory(subjects)
        tt.fill_remaining(subjects)

        generated_table = tt.table

    return render_template("index.html",
                           timetable=generated_table,
                           department=department,
                           semester=semester,
                           section=section)


@app.route("/download")
def download():
    if not generated_table:
        return "No timetable generated yet!"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    styles = getSampleStyleSheet()
    elements = []

    title = f"{department} - Semester {semester} - Section {section}"
    elements.append(Paragraph("<b>WEEKLY TIME TABLE</b>", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(title, styles['Heading2']))
    elements.append(Spacer(1, 20))

    data = [["Day","P1","P2","P3","P4","P5","P6","P7","P8"]]
    days = ["Mon","Tue","Wed","Thu","Fri"]

    for i in range(5):
        row = [days[i]]
        for cell in generated_table[i]:
            safe_text = str(cell) if cell else ""
            text = f"<para align='center'>{safe_text}</para>"
            row.append(Paragraph(text, styles['Normal']))
        data.append(row)

    table = Table(data, colWidths=[60]*9)

    table.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.pink),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),

        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),10),

        ('GRID',(0,0),(-1,-1),0.5,colors.grey),

        ('LEFTPADDING',(0,0),(-1,-1),4),
        ('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ])

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer,
                     as_attachment=True,
                     download_name="timetable.pdf")

# 📊 EXCEL DOWNLOAD
@app.route("/download_excel")
def download_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "TimeTable"

    headers = ["Day","P1","P2","P3","P4","P5","P6","P7","P8"]
    ws.append(headers)

    days = ["Mon","Tue","Wed","Thu","Fri"]

    for i in range(5):
        ws.append([days[i]] + generated_table[i])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="timetable.xlsx")


if __name__ == "__main__":
    app.run(debug=True)