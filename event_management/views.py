from datetime import datetime
from typing import cast

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from user.models import User

from .models import Event, EventRegistration
from .serializers import EventRegistrationSerializer, EventSerializer
from .tasks import send_event_date_change_email, send_event_cancellation_email
from .utils import get_or_create_event_registration


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of events with optional filters for title, date, location, and organizer."
    ),
    create=extend_schema(
        description=(
            "Create a new event and optionally invite users by providing their IDs in the 'invited_users' field."
        )
    ),
    retrieve=extend_schema(description="Retrieve details of a specific event by its ID."),
    update=extend_schema(description="Update an existing event by its ID."),
    partial_update=extend_schema(description="Partially update an existing event by its ID."),
    destroy=extend_schema(description="Delete an event by its ID."),
)
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by event title (partial match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="date",
                description="Filter by year (YYYY), year and month (YYYY-MM), " "or exact date (YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="location",
                description="Filter by location (partial match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="organizer",
                description="Filter by organizer ID (exact match)",
                required=False,
                type=int,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        title = self.request.query_params.get("title", None)
        date_str = self.request.query_params.get("date", None)
        location = self.request.query_params.get("location", None)
        organizer_id = self.request.query_params.get("organizer", None)

        queryset = Event.objects.all()

        if title:
            queryset = queryset.filter(title__icontains=title)

        if date_str:
            if len(date_str) == 4:
                queryset = queryset.filter(date__year=int(date_str))

            elif len(date_str) == 7:
                year, month = map(int, date_str.split("-"))
                queryset = queryset.filter(date__year=year, date__month=month)

            elif len(date_str) == 10:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__date=date)

            else:
                raise ValueError("Invalid date format. Use YYYY, YYYY-MM, or YYYY-MM-DD.")

        if location:
            queryset = queryset.filter(location__icontains=location)

        if organizer_id:
            queryset = queryset.filter(organizer_id=organizer_id)

        return queryset

    def perform_create(self, serializer: Serializer):
        event = serializer.save(organizer=self.request.user)
        get_or_create_event_registration(event, cast(User, self.request.user))

        invited_users = getattr(serializer, "_invited_users", [])
        for user_id in invited_users:
            if user_id != self.request.user.id:
                user_qs = get_user_model().objects.filter(pk=user_id)
                if user := user_qs.first():
                    get_or_create_event_registration(event, cast(User, user), EventRegistration.Status.PENDING)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data)
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.organizer != request.user:
            raise PermissionDenied("Only the organizer can update this event.")

        old_date = instance.date
        response = super().update(request, *args, **kwargs)
        new_date = self.get_object().date

        if old_date != new_date:
            send_event_date_change_email.delay(
                event_id=instance.id,
                old_date=old_date.strftime("%Y-%m-%d %H:%M"),
                new_date=new_date.strftime("%Y-%m-%d %H:%M"),
            )

        return response

    def perform_destroy(self, instance):
        if instance.organizer != self.request.user:
            raise PermissionDenied("Only the organizer can delete this event.")

        send_event_cancellation_email.delay(event_id=instance.id)

        instance.delete()


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of event registrations for the authenticated user."),
    create=extend_schema(description="Register the authenticated user for an event."),
    retrieve=extend_schema(description="Retrieve details of a specific event registration by its ID."),
    update=extend_schema(description="Update an existing event registration by its ID."),
    partial_update=extend_schema(description="Partially update an existing event registration by its ID."),
    destroy=extend_schema(description="Cancel an event registration by its ID."),
)
class EventRegisterViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventRegistrationSerializer

    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user).select_related("event", "user")
