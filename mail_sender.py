import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]
FAMILIES_FILE = "families.json"
EMAIL_HTML = "email_template.html"
CREDENTIALS_FILE = "credentials.json"


def send_emails(assignments: list[list[str]]):
    # Load Families
    with open(FAMILIES_FILE) as file:
        families: list[list[dict[str, str]]] = json.load(file)

    # Extract email list
    emails = {person["Name"]: person["Email"]
              for family in families
              for person in family}

    # Read HTML template
    with open(EMAIL_HTML) as file:
        html = file.read()

    # Get credentials
    flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)

    # Authenticate in Google window
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)

    # Send an email to each person in the assignments list
    for recipiant, assignment in assignments:
        # Create the message
        message = MIMEMultipart()
        message['to'] = emails[recipiant]
        message['subject'] = f'Secret Santa Assignment for {recipiant}'
        message.attach(
            MIMEText(
                html
                .replace("{recipiant}", recipiant)
                .replace("{assignment}", assignment.upper()), "html"))
        create_message = {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        # Send the message
        try:
            (service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute())
            print(F'sent message to {message['to']}')
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None
