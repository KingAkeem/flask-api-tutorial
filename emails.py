import os
import requests


def send_simple_message(to, subject, body):
    domain = os.getenv("MAILGUN_DOMAIN")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", os.getenv("MAILGUN_API_KEY")),
        data={
            "from": f"Your Name <mailgun@{domain}>",
            "to": [to],
            "subject": subject,
            "text": body,
        },
    )
