from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.models import User
from user.permissions import (
    IsUserAllIsAuthenticatedReadOnly,
    AnonOnly
)
from user.serializers import UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AnonOnly,)


class UserViewSet(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserAllIsAuthenticatedReadOnly,)
