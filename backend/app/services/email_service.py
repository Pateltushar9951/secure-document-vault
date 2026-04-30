"""
app/services/email_service.py
──────────────────────────────
Sends the OTP to the user via SMTP.

If SMTP is not configured (SMTP_HOST is blank), this service is a no-op
and the OTP is only visible in the console log (DEBUG mode).
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 30px; }}
    .card {{
      background: #ffffff;
      border-radius: 8px;
      padding: 32px;
      max-width: 480px;
      margin: auto;
      box-shadow: 0 2px 8px rgba(0,0,0,.12);
    }}
    h2 {{ color: #1a1a2e; margin-top: 0; }}
    .otp {{
      font-size: 36px;
      font-weight: bold;
      letter-spacing: 8px;
      color: #e94560;
      text-align: center;
      padding: 16px;
      background: #f9f9f9;
      border-radius: 6px;
      margin: 24px 0;
    }}
    p {{ color: #555; line-height: 1.6; }}
    .footer {{ font-size: 12px; color: #aaa; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>🔐 Secure Document Vault</h2>
    <p>You requested to download <strong>{filename}</strong>.</p>
    <p>Use the following One-Time Password to complete the download:</p>
    <div class="otp">{otp}</div>
    <p>This OTP expires in <strong>{expire_minutes} minutes</strong>
       and can only be used once.</p>
    <p>If you did not request this, please ignore this email.</p>
    <div class="footer">Secure Document Vault &mdash; do not share this code.</div>
  </div>
</body>
</html>
"""


_VERIFICATION_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 30px; }}
    .card {{
      background: #ffffff;
      border-radius: 8px;
      padding: 32px;
      max-width: 480px;
      margin: auto;
      box-shadow: 0 2px 8px rgba(0,0,0,.12);
    }}
    h2 {{ color: #1a1a2e; margin-top: 0; }}
    .otp {{
      font-size: 36px;
      font-weight: bold;
      letter-spacing: 8px;
      color: #6d28d9;
      text-align: center;
      padding: 16px;
      background: #f9f9f9;
      border-radius: 6px;
      margin: 24px 0;
    }}
    p {{ color: #555; line-height: 1.6; }}
    .footer {{ font-size: 12px; color: #aaa; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>🔐 Verify Your Email</h2>
    <p>Use the following One-Time Password to verify <strong>{email}</strong> and activate your Secure Document Vault account.</p>
    <div class="otp">{otp}</div>
    <p>This OTP expires in <strong>{expire_minutes} minutes</strong>
       and can only be used once.</p>
    <p>If you did not create this account, you can ignore this email.</p>
    <div class="footer">Secure Document Vault &mdash; keep this code private.</div>
  </div>
</body>
</html>
"""


def send_otp_email(
    recipient_email: str,
    otp_code: str,
    filename: str,
) -> bool:
    """
    Send the OTP to the user via SMTP.

    Returns:
        True  — email sent successfully
        False — SMTP not configured (OTP available only in logs)
    """
    if not settings.email_configured:
        logger.info(
            "[EMAIL] Not configured -- skipping send to %s "
            "(OTP is printed to console in DEBUG mode).",
            recipient_email,
        )
        return False

    subject = "Your Secure Document Vault OTP"
    html_body = _HTML_TEMPLATE.format(
        filename=filename,
        otp=otp_code,
        expire_minutes=settings.OTP_EXPIRE_MINUTES,
    )
    plain_body = (
        f"Your OTP for '{filename}' is: {otp_code}\n"
        f"It expires in {settings.OTP_EXPIRE_MINUTES} minutes."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = recipient_email
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, recipient_email, msg.as_string())
        logger.info("📧 OTP email sent to %s", recipient_email)
        return True
    except Exception as exc:
        logger.error("📧 Failed to send OTP email to %s: %s", recipient_email, exc)
        return False


def send_verification_email(
    recipient_email: str,
    otp_code: str,
) -> bool:
    """
    Send the registration verification OTP to the user via SMTP.
    """
    if not settings.email_configured:
        logger.info(
            "[EMAIL] Not configured -- skipping verification email to %s ",
            recipient_email,
        )
        return False

    subject = "Verify your Secure Document Vault email"
    html_body = _VERIFICATION_HTML_TEMPLATE.format(
        email=recipient_email,
        otp=otp_code,
        expire_minutes=settings.OTP_EXPIRE_MINUTES,
    )
    plain_body = (
        f"Verify your Secure Document Vault email: {recipient_email}\n"
        f"Your verification OTP is: {otp_code}\n"
        f"It expires in {settings.OTP_EXPIRE_MINUTES} minutes."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = recipient_email
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, recipient_email, msg.as_string())
        logger.info("📧 Verification email sent to %s", recipient_email)
        return True
    except Exception as exc:
        logger.error("📧 Failed to send verification email to %s: %s", recipient_email, exc)
        return False
