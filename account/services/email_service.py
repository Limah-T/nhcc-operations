from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import os
             
SENDER_EMAIL = os.environ.get("SENDER_EMAIL") 


def send_mail(subject, receiver, context:dict, html_file, txt_file):
    try:
        text_message = render_to_string(txt_file, context)
        html_message = render_to_string(html_file, context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=SENDER_EMAIL,
            to=[receiver],
        )

        email.attach_alternative(
            html_message,
            "text/html",
        )

        email.send(fail_silently=False)
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")



