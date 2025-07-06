from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


@extend_schema_view(post=extend_schema(description="Create a new user account."))
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(description="Retrieve details of the authenticated user."),
    put=extend_schema(description="Update the authenticated user's details."),
    patch=extend_schema(description="Partially update the authenticated user's details."),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
