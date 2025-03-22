from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os
import json
import requests
from ecotrade.utils import requires_auth

# Send email from Microsoft SMTP
@requires_auth
def send_email(SENDER_EMAIL, PASSWORD, RECEIVER_EMAILS, CC_EMAILS=[], SUBJECT='', BODY='', ATTACHMENTS=[]):
    '''
    This function sends an email using the SMTP server of Microsoft Outlook (Office 365).
    
    Parameters:
    - SENDER_EMAIL (str): The email address used to send the email.
    - PASSWORD (str): The password or app password for the sender's email account.
    - RECEIVER_EMAILS (list): A list of recipient email addresses.
    - CC_EMAILS (list): A list of CC recipient email addresses (default is an empty list).
    - SUBJECT (str): The subject of the email.
    - BODY (str): The HTML or plain text body of the email.
    - ATTACHMENTS (list): A list of file paths to be attached to the email (default is an empty list).
    
    Example usage:
    send_email(
        SENDER_EMAIL='your_email@domain.com',
        PASSWORD='your_password',
        RECEIVER_EMAILS=['recipient1@domain.com', 'recipient2@domain.com'],
        CC_EMAILS=['cc1@domain.com', 'cc2@domain.com'],
        SUBJECT='Test Email',
        BODY='<h1>Hello, this is a test email!</h1>',
        ATTACHMENTS=['file1.pdf', 'image.png']
    )
    '''
    for receiver_email in RECEIVER_EMAILS:
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = receiver_email
        message['Cc'] = ', '.join(CC_EMAILS)
        message['Subject'] = SUBJECT
        
        message.attach(MIMEText(BODY, 'html'))
        
        for file_path in ATTACHMENTS:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                    message.attach(part)
            else:
                print(f"Warning: Attachment '{file_path}' not found and will be skipped.")
        
        try:
            with smtplib.SMTP('smtp.office365.com', 587) as server:
                server.starttls()
                server.login(SENDER_EMAIL, PASSWORD)
                server.sendmail(SENDER_EMAIL, [receiver_email] + CC_EMAILS, message.as_string())
            print(f"Email sent successfully to {receiver_email} with CC to {', '.join(CC_EMAILS)}!")
        except Exception as e:
            print(f"Error sending email to {receiver_email}: {e}")

# Send teams notifications using Microsoft Webhook
@requires_auth
def send_teams_notification(WEBHOOK_URL, MESSAGE):
    """
    Sends a notification message to a Microsoft Teams channel using an incoming webhook.

    Parameters:
    - WEBHOOK_URL (str): The Microsoft Teams webhook URL to send the message.
    - MESSAGE (str): The text message to be sent to the Teams channel.

    Example usage:
    send_teams_notification(
        WEBHOOK_URL='https://outlook.office.com/webhook/your_webhook_url',
        MESSAGE='This is a test notification from Python!'
    )

    The function formats the message as JSON and sends it to the specified webhook.
    If the request is successful, it prints a success message; otherwise, it prints an error message.
    """
    MESSAGE = {
        "text": MESSAGE,
    }
    json_message = json.dumps(MESSAGE)
    response = requests.post(
        WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json_message
    )
    if response.status_code == 200:
        print("Teams notification sent successfully")
    else:
        print(
            f"Failed to send message. Status code: {response.status_code}, Response: {response.text}"
        )