"""Email utilities for ColabVerse account verification and recovery."""

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from django.conf import settings


def send_account_email(subject, body, recipient):
    """
    Send ColabVerse account emails through Resend.

    Used for:
    - Email verification.
    - Password recovery.
    - Future account notifications.
    """

    # Get the Resend API key from the environment.
    api_key = os.environ.get("RESEND_API_KEY")

    if not api_key:
        raise RuntimeError("RESEND_API_KEY is not configured.")

    # Get the verified sender address.
    sender = settings.CODEVIEW_EMAIL_FROM

    # Prepare the email data.
    payload = {
        "from": sender,
        "to": [recipient],
        "subject": subject,
        "text": body,
    }

    # Convert the email data to JSON.
    data = json.dumps(payload).encode("utf-8")

    # Prepare the HTTPS request.
    request = Request(
        url="https://api.resend.com/emails",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    # Send the email through Resend.
    try:
        with urlopen(request, timeout=20) as response:
            response_data = json.loads(response.read().decode("utf-8"))

        # Return 1 to indicate successful submission.
        return 1

    except HTTPError as error:
        error_details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Resend email delivery failed: {error_details}"
        ) from error