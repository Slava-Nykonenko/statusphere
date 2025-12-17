from django.urls import path, include
from rest_framework_nested.routers import NestedSimpleRouter
from rest_framework.routers import DefaultRouter

from social_media.views import (
    PostViewSet,
    CommentViewSet,
    ReactionViewSet,
    RepostViewSet,
    HashtagViewSet,
)

router = DefaultRouter()
router.register("posts", PostViewSet)
router.register("hashtags", HashtagViewSet)
posts_router = NestedSimpleRouter(router, "posts", lookup="post")
posts_router.register("comments", CommentViewSet, basename="post-comments")
posts_router.register("reactions", ReactionViewSet, basename="post-reactions")
posts_router.register("reposts", RepostViewSet, basename="post-reposts")

app_name = "social_media"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
]
