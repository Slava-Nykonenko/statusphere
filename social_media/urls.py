from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social_media.views import NewsFeed


router = DefaultRouter()
router.register("newsfeed", NewsFeed)

app_name = "social_media"

urlpatterns = [
    path("", include(router.urls)),
]
