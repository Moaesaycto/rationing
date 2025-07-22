from datetime import date, datetime
import os
from email.message import EmailMessage
from email.mime.image import MIMEImage
import smtplib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dotenv import load_dotenv
import io
import uuid

from functions.auth import get_creds
from functions.os import get_resource_path

ID = get_creds("")

REPLACEMENTS = {
    "NAME": f"{ID['name']} ({ID["identifier"]})",
    "TODAY": date.today().strftime("%A, %x"),
    "NOW": datetime.now().isoformat(),
    "AUTHORIZED": "F. BAKARR (Proxy)",
    "YEAR": date.today().strftime('%Y'),
    "UUID": str(uuid.uuid4()),
}

def create_pdf_from_text(text: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Courier", 10)

    width, height = letter
    x, y = 40, height - 40
    line_height = 12

    for line in text.splitlines():
        c.drawString(x, y, line)
        y -= line_height
        if y < 40:
            c.showPage()
            c.setFont("Courier", 10)
            y = height - 40

    c.save()
    buffer.seek(0)
    return buffer.read()

def send_custom_email(message: str):
    load_dotenv()
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')
    user_email = os.getenv('USER_EMAIL_ADDRESS')

    msg = EmailMessage()
    msg['Subject'] = 'Status Report for ' + date.today().strftime("%A, %x")
    msg['From'] = f"Aegis HQ"
    msg['To'] = user_email

    with open(get_resource_path('templates/email_template.html'), 'r', encoding='utf-8') as f:
        html_content = f.read()

    for key, value in REPLACEMENTS.items():
        html_content = html_content.replace(f"{{{{{key}}}}}", value)
    msg.set_content(
        "Attached is your status report as both a PDF and plain text.")
    msg.add_alternative(html_content, subtype='html')

    for img_path, cid in [('templates/logo.png', 'logo_img'), ('templates/warning.png', 'warning_img')]:
        with open(get_resource_path(img_path) if 'templates' in img_path else img_path, "rb") as img:
            image = MIMEImage(img.read())
            image.add_header('Content-ID', f'<{cid}>')
            image.add_header('Content-Disposition', 'inline', filename=os.path.basename(img_path))
            msg.get_payload()[1].add_related(image)

    txt_bytes = message.encode('utf-8')
    msg.add_attachment(
        txt_bytes,
        maintype='text',
        subtype='plain',
        filename=f'report-{REPLACEMENTS["NOW"]}.txt'
    )

    pdf_bytes = create_pdf_from_text(message)
    msg.add_attachment(
        pdf_bytes,
        maintype='application',
        subtype='pdf',
        filename=f'report-{REPLACEMENTS["NOW"]}.pdf'
    )

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)
