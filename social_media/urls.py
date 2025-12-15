from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social_media.views import NewsFeed, CommentViewSet

router = DefaultRouter()
router.register("newsfeed", NewsFeed)
router.register("comments", CommentViewSet)


app_name = "social_media"

urlpatterns = [
    path("", include(router.urls)),
]
