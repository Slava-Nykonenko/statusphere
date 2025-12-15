from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from social_media.models import Post, Comment, Reaction
from social_media.serializers import (
    PostSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    CommentSerializer,
    ReactionSerializer,
    RepostSerializer,
    RepostMakeSerializer,
)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.annotate(
                likes=Count("reactions"),
                shares=Count("reposts"),
                comments_num=Count("comments"),
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        serializer.save(author=self.request.user, post=post)


class ReactionViewSet(ModelViewSet):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        model_name = serializer.validated_data.pop("object_type")
        object_id = serializer.validated_data.pop("object_id")
        reaction_type = serializer.validated_data["type"]

        content_type = ContentType.objects.get(model=model_name)
        reaction, created = Reaction.objects.update_or_create(
            author=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={"type": reaction_type},
        )

        return Response(
            ReactionSerializer(reaction).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class RepostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = RepostMakeSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        serializer.save(author=self.request.user, shared_post=post)
