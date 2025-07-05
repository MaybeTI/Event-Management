from event_management.models import Event, EventRegistration
from user.models import User

from .tasks import send_event_registration_email


def get_or_create_event_registration(
    event: Event,
    user: User,
    status: EventRegistration.Status = EventRegistration.Status.CONFIRMED
) -> None:
    """
    Retrieves an existing event registration for the user or creates a new one.
    If created, the registration status is set to 'CONFIRMED' or 'PENDING' based on the 'status' parameter.
    Sends a registration email if a new registration is created.
    """
    registration, created = EventRegistration.objects.get_or_create(
        event=event, user=user, defaults={"status": status}
    )
    if created:
        send_event_registration_email.delay(user.id, event.id)
