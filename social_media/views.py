from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Q
from django.db.models.aggregates import Count
from rest_framework import status, mixins
from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from social_media.models import Post, Comment, Reaction, Hashtag
from social_media.permissions import IsAuthorAllIsAuthenticatedReadOnly
from social_media.serializers import (
    PostSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    CommentSerializer,
    ReactionSerializer,
    RepostMakeSerializer,
    RepostSerializer,
    SharedPostSerializer,
)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorAllIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Post.objects.optimized().with_counts().order_by("-created_at")

        if self.action == "list":
            content = self.request.query_params.get("content")
            hashtag = self.request.query_params.get("hashtag")
            author_id = self.request.query_params.get("author_id")

            if content or hashtag or author_id:
                if author_id == "me":
                    queryset = queryset.filter(author=self.request.user)
                elif author_id:
                    queryset = queryset.filter(author__id=author_id)

                if content:
                    queryset = queryset.filter(content__icontains=content)

                if hashtag:
                    queryset = queryset.filter(hashtag__icontains=hashtag)

                return queryset.distinct()

            return queryset.for_user_feed(self.request.user).prefetch_related(
                "hashtags"
            )

        if self.action == "retrieve":
            return queryset.prefetch_related(
                "hashtags",
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
    permission_classes = (IsAuthorAllIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Comment.objects.select_related("author", "post").prefetch_related(
            "reactions"
        )
        return queryset.order_by("created_at")

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        serializer.save(author=self.request.user, post=post)


class ReactionViewSet(ModelViewSet):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = (IsAuthorAllIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Reaction.objects.select_related("author")
        return queryset

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
    permission_classes = (IsAuthorAllIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RepostSerializer
        elif self.action == "retrieve":
            return SharedPostSerializer
        return RepostMakeSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(
            shared_post_id=int(self.kwargs["post_pk"])
        ).prefetch_related("author")
        return queryset

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        serializer.save(author=self.request.user, shared_post=post)
