import smtplib
import ssl
from email.message import EmailMessage
from flask import url_for, request

# Code and how to taken from https://towardsdatascience.com/how-to-easily-automate-emails-with-python-8b476045c151


def reset_password_mail(reciever_mail, user_id):
    email_sender = 'coffeerecommendationsofficial@gmail.com'
    email_password = 'rmsccewfojdbipbo'
    email_receiver = reciever_mail

    subject = 'Reset Password'
    domain_dynamic = request.url_root
    # url = url_for('reset_password', user_id=user_id)
    url = '/reset_password/' + user_id
    body = f"""To reset your password, click on this link {domain_dynamic + url[1:]}
Do Not reply to this e-mail."""

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
