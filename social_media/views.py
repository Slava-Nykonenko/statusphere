from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet

from social_media.models import Post
from social_media.serializers import (
    PostSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
)


class NewsFeed(ModelViewSet):
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
