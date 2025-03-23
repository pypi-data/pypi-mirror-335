import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
from writeup.utils.text_utils import draw_wrapped_text

def save_report_as_pdf(feedback, position: str, seniority: str, output: str) -> None:
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    margin = inch
    y = height - margin

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Candidate CV Evaluation Report")
    y -= 28

    # Basic info
    c.setFont("Helvetica", 12)
    c.drawString(margin, y, f"Position: {position}, Seniority: {seniority}")
    y -= 20
    c.drawString(margin, y, f"Score: {feedback.score}")
    y -= 20
    c.drawString(margin, y, f"Years of Experience: {feedback.years_experience}")
    y -= 20

    # Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Summary:")
    y -= 15
    c.setFont("Helvetica", 12)
    y = draw_wrapped_text(c, feedback.summary, margin, y, width - 2 * margin, 15)

    # Relevant Skills
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Relevant Skills:")
    y -= 15
    c.setFont("Helvetica", 12)
    y = draw_wrapped_text(c, ", ".join(feedback.relevant_skills), margin, y, width - 2 * margin, 15)

    # Other Skills
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Other Skills:")
    y -= 15
    c.setFont("Helvetica", 12)
    y = draw_wrapped_text(c, ", ".join(feedback.other_skills), margin, y, width - 2 * margin, 15)

    # Pros
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Pros:")
    y -= 15
    c.setFont("Helvetica", 12)
    for pro in feedback.pros:
        y = draw_wrapped_text(c, f"• {pro}", margin, y, width - 2 * margin, 15)

    # Cons
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Cons:")
    y -= 15
    c.setFont("Helvetica", 12)
    for con in feedback.cons:
        y = draw_wrapped_text(c, f"• {con}", margin, y, width - 2 * margin, 15)

    c.showPage()
    c.save()

def save_batch_report_as_pdf(reports: list, position: str, seniority: str, output: str) -> None:
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]

    # Sort reports by score descending
    sorted_reports = sorted(reports, key=lambda x: x["score"], reverse=True)

    # Generate a bar chart using matplotlib
    files = [rep["file"] for rep in sorted_reports]
    scores = [rep["score"] for rep in sorted_reports]

    plt.figure(figsize=(8, 4))
    plt.bar(files, scores)
    plt.title(f"Scores for {seniority} {position}")
    plt.xlabel("CV Files")
    plt.ylabel("Scores")
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    chart_image = ImageReader(img_buffer)

    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    margin = inch
    y = height - margin

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, f"Batch CV Evaluation Results: {seniority} {position}")
    y -= 28

    # Place the bar chart
    c.drawImage(chart_image, margin, y - 250, width=400, height=250, preserveAspectRatio=True)
    y -= 270

    # Create table data including Years of Experience
    data = [["File", "Score", "Years Exp", "Summary"]]
    for rep in sorted_reports:
        file_para = Paragraph(rep["file"], styleN)
        summary_para = Paragraph(rep["summary"], styleN)
        data.append([file_para, f"{rep['score']:.1f}", str(rep.get("years_experience", "")), summary_para])

    available_width = width - 2 * margin
    col_widths = [2 * inch, 1 * inch, 1 * inch, available_width - 4 * inch]

    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    
    table_width, table_height = table.wrap(available_width, y)
    if y - table_height < margin:
        c.showPage()
        y = height - margin
    table.drawOn(c, margin, y - table_height)
    y = y - table_height - 20

    c.showPage()
    c.save()
