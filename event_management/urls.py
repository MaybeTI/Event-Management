from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventRegisterViewSet, EventViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"events_register", EventRegisterViewSet, basename="event_register")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "event_management"
