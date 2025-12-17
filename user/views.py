from django.db.models import Value, CharField
from django.db.models.functions import Concat
from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from django.utils.translation import gettext as _

from user.models import User
from user.permissions import IsUserAllIsAuthenticatedReadOnly, AnonOnly
from user.serializers import (
    UserSerializer,
    UserRetrieveSerializer,
    UserListSerializer
)


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AnonOnly,)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserAllIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "following", "posts", "posts__hashtags"
            )

        elif self.action == "list":
            search_query = self.request.query_params.get("search")
            if search_query:
                return queryset.annotate(
                    full_name=Concat(
                        "first_name", Value(" "), "last_name", output_field=CharField()
                    )
                ).filter(full_name__icontains=search_query)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        return UserSerializer

    @action(detail=True, methods=["get"], url_path="toggle-follow")
    def toggle_follow(self, request, pk=None):
        user_to_follow = self.get_object()
        me = request.user
        print("user_to_follow", user_to_follow)
        print("me", me)
        if user_to_follow == me:
            return Response(
                {"error": _("You cannot follow yourself")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_to_follow in me.following.all():
            me.following.remove(user_to_follow)
            return Response({"status": _("Unfollowed")}, status=status.HTTP_200_OK)

        me.following.add(user_to_follow)
        return Response({"status": _("Followed")}, status=status.HTTP_200_OK)
