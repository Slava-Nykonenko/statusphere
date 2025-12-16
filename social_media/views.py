from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from social_media.models import Post, Comment, Reaction
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
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "author", "shared_post", "hashtags", "reposts"
            )
            if self.action == "retrieve":
                comment_reactions_prefetch = Prefetch(
                    "reactions", queryset=Reaction.objects.select_related("author")
                )

                comments_prefetch = Prefetch(
                    "comments",
                    queryset=Comment.objects.select_related("author").prefetch_related(
                        comment_reactions_prefetch
                    ),
                )

                reactions_prefetch = Prefetch(
                    "reactions", queryset=Reaction.objects.select_related("author")
                )

                queryset = queryset.select_related(
                    "shared_post__author"
                ).prefetch_related(
                    comments_prefetch,
                    reactions_prefetch,
                    "reposts__author",
                )

            queryset = queryset.annotate(
                likes=Count("reactions", distinct=True),
                shares=Count("reposts", distinct=True),
                comments_num=Count("comments", distinct=True),
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
        return queryset

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
