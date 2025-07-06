from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Event, EventRegistration


@shared_task
def send_event_registration_email(user_id: int, event_id: int) -> None:
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
    registration = EventRegistration.objects.get(user_id=user_id, event_id=event_id)
    status = registration.status

    email_content = {
        EventRegistration.Status.CONFIRMED: (
            f"Registration Confirmed: {event.title}",
            f"Hi {user.email},\n\n"
            f"Your registration for the event '{event.title}' "
            f"on {event.date.strftime('%Y-%m-%d %H:%M')} has been confirmed.",
        ),
        EventRegistration.Status.CANCELLED: (
            f"Registration Cancelled: {event.title}",
            f"Hi {user.email},\n\n"
            f"Your registration for the event '{event.title}' "
            f"on {event.date.strftime('%Y-%m-%d %H:%M')} has been cancelled.",
        ),
    }

    subject, message = email_content.get(
        EventRegistration.Status(status),
        (
            f"Invitation to Event: {event.title}",
            f"Hi {user.email},\n\n"
            f"You have been invited to the event '{event.title}' "
            f"scheduled for {event.date.strftime('%Y-%m-%d %H:%M')}. "
            f"Please confirm your participation.",
        ),
    )

    send_mail(subject=subject, message=message, from_email="noreply@gmail.com", recipient_list=[user.email])


@shared_task
def send_event_date_change_email(event_id: int, old_date: str, new_date: str) -> None:
    """
    Send an email notification to all participants (including the organizer)
    about the change in event date.
    """
    event = Event.objects.prefetch_related("registrations__user").get(pk=event_id)

    subject = f"Updated Date for Event: {event.title}"
    message = (
        f"Hello,\n\n"
        f"The date for the event '{event.title}' has been updated.\n\n"
        f"Previous Date: {old_date}\n"
        f"New Date: {new_date}\n\n"
        f"Please make note of this change in your calendar.\n\n"
        f"Thank you!"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email="noreply@gmail.com",
        recipient_list=[reg.user.email for reg in event.registrations.all()],
    )


@shared_task
def send_event_cancellation_email(event_title: str, event_date: str, participant_emails: list) -> None:
    """
    Send an email notification to all participants about the cancellation of an event.

    Parameters:
        event_title (str): The title of the event being canceled.
        event_date (str): The date of the event being canceled.
        participant_emails (list): A list of email addresses of participants.
    """
    subject = f"Event Cancelled: {event_title}"
    message = (
        f"Hello,\n\n"
        f"We regret to inform you that the event '{event_title}' scheduled for "
        f"{event_date} has been cancelled.\n\n"
        f"Thank you for your understanding."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email="noreply@gmail.com",
        recipient_list=participant_emails,
    )
