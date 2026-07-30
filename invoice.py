"""
ReportLab Invoice Generation Module for Bizflow AI CRM (Per-User Isolated)
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from config import INVOICES_DIR
from models import get_sale_details, add_invoice_record

def format_pdf_date(date_str):
    if not date_str:
        return datetime.now().strftime("%d %b %Y, %I:%M %p")
    try:
        dt = datetime.strptime(str(date_str)[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(date_str)

def generate_pdf_invoice(sale_id, user_id):
    sale = get_sale_details(sale_id, user_id)
    if not sale:
        raise ValueError(f"Sale ID {sale_id} not found or does not belong to your account.")

    filename = f"Invoice_SALE_{sale_id}_{int(datetime.now().timestamp())}.pdf"
    filepath = str(INVOICES_DIR / filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=4
    )

    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#374151')
    )

    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#111827')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#1F2937')
    )
    
    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1
    )

    table_cell_right = ParagraphStyle(
        'TableCellRight',
        parent=table_cell_style,
        alignment=2
    )

    elements = []

    formatted_date = format_pdf_date(sale.get('date'))
    payment_method = sale.get('payment_method') or 'Cash'

    # Header section
    header_data = [
        [
            Paragraph("<b>BIZFLOW STORE</b><br/>Customer Relationship & Invoice System", subtitle_style),
            Paragraph(f"<b>INVOICE RECEIPT</b><br/><font size=9 color='#6B7280'>Inv #: INV-{sale_id:04d}<br/>Date: {formatted_date}</font>", ParagraphStyle('RHeader', parent=subtitle_style, alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4F46E5'), spaceAfter=15))

    # Customer & Business Info
    cust_info = f"""
    <b>Billed To:</b><br/>
    <b>{sale['customer_name']}</b><br/>
    Phone: {sale['customer_phone']}<br/>
    Email: {sale['customer_email'] or 'N/A'}<br/>
    Address: {sale['customer_address'] or 'N/A'}
    """
    
    biz_info = f"""
    <b>Issued By:</b><br/>
    <b>Bizflow Store</b><br/>
    Main Street Business Hub<br/>
    Support: +91 98765 43210<br/>
    Email: support@bizflowcrm.com
    """

    info_data = [
        [Paragraph(cust_info, normal_style), Paragraph(biz_info, normal_style)]
    ]
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # Itemized Table
    items_table_data = [
        [
            Paragraph("#", table_header_style),
            Paragraph("Item & Description", table_header_style),
            Paragraph("Qty", table_header_style),
            Paragraph("Unit Price (Rs.)", table_header_style),
            Paragraph("Subtotal (Rs.)", table_header_style)
        ]
    ]

    subtotal_sum = 0.0
    for idx, item in enumerate(sale['items'], 1):
        subtotal_sum += item['subtotal']
        items_table_data.append([
            Paragraph(str(idx), table_cell_center),
            Paragraph(f"<b>{item['product_name']}</b>", table_cell_style),
            Paragraph(str(item['quantity']), table_cell_center),
            Paragraph(f"{item['unit_price']:.2f}", table_cell_right),
            Paragraph(f"{item['subtotal']:.2f}", table_cell_right)
        ])

    items_table = Table(items_table_data, colWidths=[0.4*inch, 3.4*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F46E5')),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FAFB')])
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # Totals Summary Table
    discount = sale.get('discount', 0.0)
    grand_total = sale['total_amount']

    summary_data = [
        [Paragraph("Items Subtotal:", bold_style), Paragraph(f"Rs. {subtotal_sum:.2f}", ParagraphStyle('R', parent=bold_style, alignment=2))],
        [Paragraph("Discount Applied:", normal_style), Paragraph(f"- Rs. {discount:.2f}", ParagraphStyle('R', parent=normal_style, alignment=2))],
        [Paragraph("Payment Method:", normal_style), Paragraph(f"<b>{payment_method}</b> (Paid In Full)", ParagraphStyle('RMethod', parent=normal_style, alignment=2, textColor=colors.HexColor('#059669')))],
        [Paragraph("<b>Grand Total:</b>", title_style), Paragraph(f"<b>Rs. {grand_total:.2f}</b>", ParagraphStyle('RT', parent=title_style, fontSize=16, alignment=2))]
    ]
    summary_table = Table(summary_data, colWidths=[4.8*inch, 2.2*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0,3), (-1,3), 1, colors.HexColor('#4F46E5')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 25))

    footer_text = f"""
    <b>Thank you for your business!</b><br/>
    Payment Status: <b>PAID VIA {payment_method.upper()}</b> • Terms: Payment received with thanks. This is an official computer-generated tax invoice.
    """
    elements.append(Paragraph(footer_text, subtitle_style))

    doc.build(elements)

    add_invoice_record(user_id, sale_id, sale['customer_id'], filepath, grand_total)

    return filename, filepath
