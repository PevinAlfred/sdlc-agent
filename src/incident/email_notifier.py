
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger

def send_email_notification(smtp_server, port, user, password, incident_data):
    """
    Send an email notification for the incident using real SMTP logic.
    incident_data must include 'recipient', 'title', and 'description'.
    """
    try:
        logger.info("Sending email notification...")
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = incident_data.get('recipient')
        msg['Subject'] = incident_data.get('title', 'Incident Notification')
        msg.attach(MIMEText(incident_data.get('description', ''), 'plain'))

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, incident_data.get('recipient'), msg.as_string())
        logger.info("Email notification sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        raise
