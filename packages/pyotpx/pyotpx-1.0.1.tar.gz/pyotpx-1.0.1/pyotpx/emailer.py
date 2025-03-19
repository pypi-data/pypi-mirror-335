import smtplib
import ssl
from email.mime.text import MIMEText

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "PyOTPX@gmail.com"
SENDER_PASSWORD = "qrte glkd lbri svox"  # App Password

def send_otp(to_email, otp):
    """Sends an OTP to the specified email."""
    msg = MIMEText(f"Your OTP Code is: {otp}\n\nThis OTP is valid for 5 minutes.")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print("❌ Failed to send email:", e)
        return False
