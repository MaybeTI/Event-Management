from django.contrib.auth import get_user_model
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="organized_events")

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        unique_together = ("event", "user")
        ordering = ["event__date"]

    def __str__(self):
        return f"{self.user.email} – {self.event.title} – {self.status}"
