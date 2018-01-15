# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import sendgrid
from base import app
from sendgrid.helpers.mail import *


def send_email(subject, content, recipient):
    api_key = app.config.get('SENDGRID_API_KEY')['api-key']
    sg = sendgrid.SendGridAPIClient(apikey=api_key)
    from_email = Email("no-reply@upvote.pub")
    to_email = Email(recipient)
    content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response

