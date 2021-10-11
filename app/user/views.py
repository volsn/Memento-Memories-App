from typing import Any

from django.utils.translation import gettext as _
from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.mixins import UpdateModelMixin
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.request import Request

from user.serializers import UserSerializer, AuthTokenSerializer
from core.models import User


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateDestroyAPIView, UpdateModelMixin):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> User:
        """Retrieve and return authentication user"""
        return self.request.user

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Partial update of user"""
        return self.partial_update(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override delete method to return message response"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': _('User successfully deleted')},
                        status=status.HTTP_200_OK)
