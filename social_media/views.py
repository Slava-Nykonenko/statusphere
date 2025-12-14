from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet

from social_media.models import Post
from social_media.serializers import PostSerializer, PostListSerializer


class NewsFeed(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.annotate(
                likes=Count("liked_by"),
                shares=Count("shared_by"),
                comments_num=Count("comments"),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
