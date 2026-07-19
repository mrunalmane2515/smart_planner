from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def generate_project_report(project, tasks, filename):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        f"<b>{project.name} - Task Report</b>",
        styles["Title"]
    )

    elements.append(title)
    elements.append(Paragraph("<br/>", styles["Normal"]))

    data = [
        [
            "Title",
            "Status",
            "Priority",
            "Due Date"
        ]
    ]

    for task in tasks:

        due = ""

        if task.due_date:
            due = task.due_date.strftime("%d-%m-%Y")

        data.append([
            task.title,
            task.status,
            task.priority,
            due
        ])

    table = Table(data, colWidths=[2.8*inch, 1.4*inch, 1.2*inch, 1.4*inch])

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),

        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0,0), (-1,0), 10),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

    ]))

    elements.append(table)

    doc.build(elements)