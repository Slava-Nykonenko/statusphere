from django.db.models import Value, CharField, Count, Exists, OuterRef
from django.db.models.functions import Concat
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.utils.translation import gettext as _

from user.models import User
from user.permissions import IsUserAllIsAuthenticatedReadOnly, AnonOnly
from user.serializers import UserSerializer, UserRetrieveSerializer, UserListSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AnonOnly,)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserAllIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = User.objects.all()
        if self.action in ("list", "retrieve", "followers", "following"):
            if self.action == "list":
                search_query = self.request.query_params.get("user")
                if search_query:
                    queryset = queryset.annotate(
                        full_name=Concat(
                            "first_name",
                            Value(" "),
                            "last_name",
                            output_field=CharField(),
                        )
                    ).filter(full_name__icontains=search_query)

            queryset = queryset.annotate(
                followers_count=Count("followers", distinct=True),
                following_count=Count("following", distinct=True),
                is_following=Exists(
                    self.request.user.following.filter(pk=OuterRef("pk"))
                ),
                is_followers=Exists(
                    self.request.user.followers.filter(pk=OuterRef("pk"))
                ),
            ).order_by("-followers_count")

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "followers", "following"):
            return UserListSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        elif self.action == "me":
            return UserSerializer
        return UserSerializer

    @extend_schema(
        summary="Retrieve or update the authenticated user's own profile",
        responses={200: UserSerializer},
    )
    @action(detail=False, methods=["get", "put", "patch"], url_path="me")
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="toggle-follow")
    def toggle_follow(self, request, pk=None):
        user_to_follow = self.get_object()
        me = request.user

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

    @action(detail=True, methods=["get"], url_path="followers")
    def followers(self, request, pk=None):
        user = self.get_object()
        followers = self.get_queryset().filter(following=user).order_by("first_name")

        page = self.paginate_queryset(followers)
        serializer = self.get_serializer(page or followers, many=True)
        return (
            self.get_paginated_response(serializer.data)
            if page
            else Response(serializer.data)
        )

    @action(detail=True, methods=["get"], url_path="following")
    def following(self, request, pk=None):
        user = self.get_object()
        following = self.get_queryset().filter(followers=user).order_by("first_name")

        page = self.paginate_queryset(following)
        serializer = self.get_serializer(page or following, many=True)
        return (
            self.get_paginated_response(serializer.data)
            if page
            else Response(serializer.data)
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user",
                type={"type": "string"},
                description="Find users by first, last or full name. This is "
                "case-insensitive and performs a partial match "
                "(i.e. '?user=albert', or '?user=einst', or "
                "'?user=albert%20einstein' will find 'Albert Einstein').",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
