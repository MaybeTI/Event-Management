from typing import Literal

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Event


@shared_task
def send_event_registration_email(
    user_id: int,
    event_id: int,
    status: Literal["pending", "confirmed", "cancelled"] = "confirmed",
) -> None:
    """
    Send an email notification to the user about their event registration status.

    Parameters:
        user_id (int): The ID of the user to notify.
        event_id (int): The ID of the event.
        status (Literal["pending", "confirmed", "cancelled"], optional):
            The registration status. The email content will vary depending on the status.
            Defaults to "confirmed".
    """
    user = get_user_model().objects.get(pk=user_id)
    event = Event.objects.get(pk=event_id)

    if status == "confirmed":
        subject = f"Registration Confirmed: {event.title}"
        message = (
            f"Hi {user.email},\n\n"
            f"Your registration for the event '{event.title}' "
            f"on {event.date.strftime('%Y-%m-%d %H:%M')} has been confirmed."
        )
    elif status == "cancelled":
        subject = f"Registration Cancelled: {event.title}"
        message = (
            f"Hi {user.email},\n\n"
            f"Your registration for the event '{event.title}' "
            f"on {event.date.strftime('%Y-%m-%d %H:%M')} has been cancelled."
        )
    else:
        subject = f"Invitation to Event: {event.title}"
        message = (
            f"Hi {user.email},\n\n"
            f"You have been invited to the event '{event.title}' "
            f"scheduled for {event.date.strftime('%Y-%m-%d %H:%M')}. "
            f"Please confirm your participation."
        )

    send_mail(
        subject=subject,
        message=message,
        from_email="noreply@gmail.com",
        recipient_list=[user.email],
    )
