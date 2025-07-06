from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "user_email",
            "event",
            "registered_at",
            "status",
        ]

    def create(self, validated_data):
        instance = super().create(validated_data)
        send_event_registration_email.delay(user_id=instance.user.id, event_id=instance.event.id)
        return instance

    def update(self, instance, validated_data):
        registration = super().update(instance, validated_data)
        if "status" in validated_data:
            send_event_registration_email.delay(user_id=registration.user.id, event_id=registration.event.id)
        return registration
