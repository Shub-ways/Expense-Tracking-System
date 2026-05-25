import os
import aiosmtplib
from email.message import EmailMessage
from logging_setup import setup_logger

logger = setup_logger("email_service")

# Note: In production, never commit real passwords.
# Always load them from environment variables via Hugging Face Space secrets.
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # e.g. App Password for Gmail

async def _send_email_async(to_email: str, subject: str, body_html: str):
    """Internal helper to connect to SMTP and send an email."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning(f"SMTP credentials not configured. Skipping email to {to_email}")
        return False

    message = EmailMessage()
    message["From"] = f"Expense Tracker <{SMTP_USERNAME}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body_html, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
        )
        logger.info(f"Successfully sent email '{subject}' to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def send_welcome_email(to_email: str, username: str):
    """Send a welcome email upon successful registration."""
    subject = "Welcome to Expense Tracking System! 🎉"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #1E293B;">
            <div style="text-align: center; padding: 20px;">
                <h1 style="color: #2563EB;">Welcome, {username}!</h1>
                <p style="font-size: 16px;">We're thrilled to have you onboard.</p>
                <p style="font-size: 16px;">Log in to track your expenses and start saving today.</p>
                <br/>
                <p style="color: #64748B; font-size: 14px;">The Expense Tracker Team</p>
            </div>
        </body>
    </html>
    """
    return await _send_email_async(to_email, subject, body)


async def send_budget_alert(to_email: str, category: str, limit: float, spent: float, currency: str = "₹"):
    """Send an alert when a budget is exceeded."""
    subject = f"🚨 Budget Exceeded for {category}!"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #1E293B;">
            <div style="padding: 20px; border: 1px solid #FCA5A5; border-radius: 8px; background-color: #FEF2F2;">
                <h2 style="color: #DC2626;">Budget Alert</h2>
                <p style="font-size: 16px;">You have exceeded your monthly budget for <b>{category}</b>.</p>
                <ul style="font-size: 16px;">
                    <li><b>Budget Limit:</b> {currency}{limit:,.2f}</li>
                    <li><b>Total Spent:</b> {currency}{spent:,.2f}</li>
                </ul>
                <p style="font-size: 16px;">Please review your dashboard to adjust your spending.</p>
            </div>
        </body>
    </html>
    """
    return await _send_email_async(to_email, subject, body)
