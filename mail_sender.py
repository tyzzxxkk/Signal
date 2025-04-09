from flask_mail import Message
from extensions import mail
from filters import filter_bad_words
from flask import current_app

def send_letter_mail(receiver_email, subject, sender_name, content):
    content = filter_bad_words(content)
    msg = Message(subject=subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[receiver_email])
    msg.body = f"[From] {sender_name}\n\n{content}"
    mail.send(msg)
