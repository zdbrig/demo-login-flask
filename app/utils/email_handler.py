import smtplib
import os
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailHandler:
    def __init__(self):
        # Get email credentials and SMTP server details from environment variables
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, subject, message, email_to, files=None):
        # Ensure email_to is a list
        if not isinstance(email_to, list):
            email_to = [email_to]

        # Create an email message object
        if files:
            msg = MIMEMultipart()
            msg.attach(MIMEText(message, 'plain'))

            # Attach files to the email
            for f in files:
                with open(f, 'rb') as fp:
                    part = MIMEApplication(fp.read(), Name=os.path.basename(f))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(f)}"'
                    msg.attach(part)
        else:
            msg = EmailMessage()
            msg.set_content(message)

        # Set the email headers
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['Date'] = formatdate(localtime=True)
        msg['To'] = ", ".join(email_to)
       
       # Connect to the SMTP server and send the email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.set_debuglevel(1)  # Enable debug output for troubleshooting
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)
            print(f"Email sent successfully to {', '.join(email_to)}")
        except smtplib.SMTPRecipientsRefused as e:
            print(f"SMTPRecipientsRefused: The server refused to send the email to the recipients: {e.recipients}")
        except smtplib.SMTPException as e:
            print(f"SMTP error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while sending email: {e}")
        finally:
            server.quit()
