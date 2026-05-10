"""Email notification service — application updates, interview reminders, offer alerts."""
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

from app.core.config import settings

logger = logging.getLogger(__name__)


def _log_or_send(to_email: str, subject: str, body: str, html_body: str | None = None):
  """Send email via SMTP or log to console if SMTP not configured."""
  smtp_host = getattr(settings, 'smtp_host', '')
  smtp_port = getattr(settings, 'smtp_port', 587)

  if not smtp_host:
    logger.info(f'[EMAIL] To: {to_email} | Subject: {subject}')
    logger.info(f'[EMAIL] Body: {body[:200]}')
    return True

  try:
    import smtplib

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = getattr(settings, 'smtp_from', 'noreply@aijobhunter.local')
    msg['To'] = to_email
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    if html_body:
      msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    smtp_user = getattr(settings, 'smtp_user', '')
    smtp_password = getattr(settings, 'smtp_password', '')

    with smtplib.SMTP(smtp_host, smtp_port) as server:
      server.starttls()
      if smtp_user:
        server.login(smtp_user, smtp_password)
      server.send_message(msg)

    logger.info(f'Email sent to {to_email}: {subject}')
    return True
  except Exception as e:
    logger.error(f'Failed to send email: {e}')
    return False


async def send_application_confirmation(
  user_email: str,
  company: str,
  role: str,
  batch_number: int,
) -> bool:
  """Notify user that an application has been submitted."""
  subject = f'Application Submitted: {role} at {company}'
  body = f'''Your application has been submitted!

Company: {company}
Role: {role}
Date: {date.today().isoformat()}
Batch: #{batch_number}

Your application is now in the Kanban board. We'll notify you when there's an update.

—
AI Job Hunter
https://aijobhunter.local'''

  html_body = f'''<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #1e40af;">Application Submitted</h2>
  <p>Your application has been sent:</p>
  <table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
    <tr><td style="padding: 4px 0; color: #6b7280;">Company</td><td style="padding: 4px 0;"><strong>{company}</strong></td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Role</td><td style="padding: 4px 0;"><strong>{role}</strong></td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Date</td><td style="padding: 4px 0;">{date.today().isoformat()}</td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Batch</td><td style="padding: 4px 0;">#{batch_number}</td></tr>
  </table>
  <p style="color: #6b7280; font-size: 12px;">AI Job Hunter · Your automated career assistant</p>
</body>
</html>'''

  return _log_or_send(user_email, subject, body, html_body)


async def send_interview_reminder(
  user_email: str,
  company: str,
  role: str,
  interview_type: str,
  scheduled_date: str | None = None,
) -> bool:
  """Send interview preparation reminder."""
  date_str = scheduled_date or 'Upcoming'
  subject = f'Interview Prep: {role} at {company}'
  body = f'''Interview Reminder

Company: {company}
Role: {role}
Type: {interview_type}
Date: {date_str}

Prepare with AI Job Hunter:
- Review company research
- Practice mock interview questions
- Check skill gap analysis
- Read salary negotiation brief

Good luck!

—
AI Job Hunter'''

  html_body = f'''<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #1e40af;">Interview Reminder</h2>
  <p>You have an upcoming interview:</p>
  <table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
    <tr><td style="padding: 4px 0; color: #6b7280;">Company</td><td><strong>{company}</strong></td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Role</td><td><strong>{role}</strong></td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Type</td><td>{interview_type}</td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Date</td><td>{date_str}</td></tr>
  </table>
  <p>Visit <a href="https://aijobhunter.local/interviews">AI Job Hunter</a> to prepare.</p>
</body>
</html>'''

  return _log_or_send(user_email, subject, body, html_body)


async def send_offer_alert(
  user_email: str,
  company: str,
  role: str,
  salary: float,
) -> bool:
  """Alert user when an offer is received."""
  subject = f'Offer Received: {role} at {company}'
  body = f'''Congratulations — you received an offer!

Company: {company}
Role: {role}
Salary: {salary:,.0f}

Next steps:
1. Evaluate this offer against others with AI analysis
2. Generate a negotiation strategy
3. Compare with market benchmarks

Visit AI Job Hunter to get started.

—
AI Job Hunter'''

  html_body = f'''<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
  <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 20px; margin: 16px 0;">
    <h2 style="color: #166534; margin: 0;">Offer Received!</h2>
    <p style="color: #15803d;">Congratulations on your offer from <strong>{company}</strong></p>
  </div>
  <table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
    <tr><td style="padding: 4px 0; color: #6b7280;">Company</td><td><strong>{company}</strong></td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Role</td><td><strong>{role}</strong></td></tr>
    <tr><td style="padding: 4px 0; color: #6b7280;">Salary</td><td><strong>{salary:,.0f}</strong></td></tr>
  </table>
  <p>Visit <a href="https://aijobhunter.local/offers">AI Job Hunter</a> to evaluate and negotiate.</p>
</body>
</html>'''

  return _log_or_send(user_email, subject, body, html_body)
