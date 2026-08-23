import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>FreshMart</b>", styles["Title"]))
    elements.append(Paragraph(f"Invoice — Order {order.order_number}", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"Date: {order.created_at.strftime('%d %b %Y')}", styles["Normal"]))
    elements.append(Paragraph(f"Payment: {order.get_payment_method_display()} ({order.payment_status})", styles["Normal"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Ship to</b>", styles["Heading3"]))
    address_lines = [
        order.shipping_name, order.shipping_line1, order.shipping_line2,
        f"{order.shipping_city}, {order.shipping_state} {order.shipping_pincode}",
        order.shipping_country, order.shipping_phone,
    ]
    for line in filter(None, address_lines):
        elements.append(Paragraph(line, styles["Normal"]))
    elements.append(Spacer(1, 14))

    data = [["Item", "Qty", "Unit Price", "Total"]]
    for item in order.items.all():
        data.append([item.product_name, str(item.quantity), f"₹{item.unit_price}", f"₹{item.line_total}"])

    table = Table(data, colWidths=[220, 60, 90, 90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B8F3C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    summary_data = [
        ["Subtotal", f"₹{order.subtotal}"],
        ["Discount", f"-₹{order.discount_amount}"],
        ["Delivery", f"₹{order.delivery_charge}"],
        ["Tax (GST)", f"₹{order.tax_amount}"],
        ["Total", f"₹{order.total}"],
    ]
    summary_table = Table(summary_data, colWidths=[420, 90])
    summary_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(summary_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
