import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_login_email(to_email, token):
    sender_email = os.getenv("EMAIL_SENDER")
    smtp_username = os.getenv("SMTP_USERNAME", sender_email)
    smtp_password = os.getenv("SMTP_PASSWORD")  # For Gmail, use App Password
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))

    if not sender_email or not smtp_password:
        raise RuntimeError("Missing EMAIL_SENDER or SMTP_PASSWORD environment variables.")

    msg = EmailMessage()
    msg['Subject'] = "Your Chatbot Login Link"
    msg['From'] = sender_email
    msg['To'] = to_email
    login_url = f"http://localhost:8501/?token={token}"
    msg.set_content(f"Click this link to log in: {login_url}")

    # SSL (465) or STARTTLS (587)
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg)
