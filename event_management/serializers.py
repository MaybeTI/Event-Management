from django.utils import timezone
from rest_framework import serializers

from .models import Event, EventRegistration
from .tasks import send_event_registration_email


class EventSerializer(serializers.ModelSerializer):
    invited_users = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=list,
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "location",
            "organizer",
            "invited_users",
        ]
        read_only_fields = ["organizer"]

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("The event date cannot be in the past.")
        return value

    def create(self, validated_data):
        invited_users = validated_data.pop("invited_users", [])
        event = Event.objects.create(**validated_data)
        self._invited_users = invited_users
        return event


class EventRegistrationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)
    event_date = serializers.DateTimeField(source="event.date", read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=EventRegistration._meta.get_field("user").related_model.objects.all(),
    )
    event = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=EventRegistration._meta.get_field("event").related_model.objects.all(),
    )

    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "user_email",
            "event_title",
            "event_date",
            "registered_at",
            "user",
            "event",
            "status",
        ]

    def create(self, validated_data):
        registration = super().create(validated_data)
        send_event_registration_email.delay(registration.user.id, registration.event.id)
        return registration

    def update(self, instance, validated_data):
        registration = super().update(instance, validated_data)
        if "status" in validated_data:
            send_event_registration_email.delay(registration.user.id, registration.event.id)
        return registration
