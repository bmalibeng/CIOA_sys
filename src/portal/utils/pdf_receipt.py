from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os
from datetime import datetime


def generate_payment_receipt(payment):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#C8102E'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=8,
        fontName='Helvetica'
    )

    center_style = ParagraphStyle(
        'CustomCenter',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=8,
        fontName='Helvetica'
    )

    elements = []

    elements.append(Paragraph("COGRABIG INSTITUTE OF ARTS", title_style))
    elements.append(Paragraph("Fashion | Photography | Filmmaking | Make-up | Dress-making | Tailoring", center_style))
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Table([['']], colWidths=[16*cm], rowHeights=[2],
                          style=TableStyle([
                              ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#C8102E')),
                              ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#C8102E')),
                          ])))
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("OFFICIAL PAYMENT RECEIPT", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    receipt_data = [
        ['Receipt Number:', payment.receipt_number],
        ['Date:', payment.payment_date.strftime('%B %d, %Y')],
        ['Received By:', payment.received_by.get_full_name() if payment.received_by else 'N/A'],
        ['Status:', payment.get_status_display()],
    ]

    receipt_table = Table(receipt_data, colWidths=[5*cm, 11*cm])
    receipt_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#C8102E')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("STUDENT INFORMATION", heading_style))
    student_data = [
        ['Student ID:', payment.student.student_id],
        ['Name:', payment.student.get_full_name()],
        ['Program:', payment.program.name],
        ['Email:', payment.student.email or 'N/A'],
        ['Phone:', payment.student.phone or 'N/A'],
    ]

    student_table = Table(student_data, colWidths=[5*cm, 11*cm])
    student_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#C8102E')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("PAYMENT DETAILS", heading_style))
    payment_data = [
        ['Program:', payment.program.name],
        ['Total Program Fees:', f"M {payment.program.total_fees:,.2f}"],
        ['Amount Paid:', f"M {payment.amount:,.2f}"],
        ['Balance Due:', f"M {payment.student.get_balance_due():,.2f}"],
    ]

    payment_table = Table(payment_data, colWidths=[5*cm, 11*cm])
    payment_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#C8102E')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 2), (1, 2), 12),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#C8102E')),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.5*cm))

    if payment.notes:
        elements.append(Paragraph("NOTES", heading_style))
        elements.append(Paragraph(payment.notes, normal_style))
        elements.append(Spacer(1, 0.5*cm))

    elements.append(Spacer(1, 1*cm))
    elements.append(Table([['']], colWidths=[16*cm], rowHeights=[1],
                          style=TableStyle([
                              ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1A1A1A')),
                              ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#1A1A1A')),
                          ])))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph("Thank you for your payment!", center_style))
    elements.append(Paragraph("For queries, contact: accounts@cioa.edu.ls | +266 1234 5678", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
