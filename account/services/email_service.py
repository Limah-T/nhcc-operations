from django.template.loader import render_to_string
from nhcc_operations.config.settings.base import env
from requests.exceptions import RequestException
import requests
             
SENDER_EMAIL = env("SENDER_EMAIL") 
URL = env("SEND_EMAIL_URL")
API_KEY = env("EMAIL_API_KEY")

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

def send_mail(subject, receiver, context:dict, html_file, txt_file):

    try:
        html = render_to_string(template_name=html_file,context=context)
        text = render_to_string(template_name=txt_file,context=context)
        payload = {
            "sender": {"email": SENDER_EMAIL, "name": "NHCC Operations"},
            "subject": subject, "to": [{"email": receiver}],
            "htmlContent": html, "textContent": text}
    except Exception as exc:
        return False   
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        print("Email sent successfully!")
    except RequestException as exc:
        print(f"An error occurred: {exc}")

