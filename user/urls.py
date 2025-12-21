from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from user.views import CreateUserView, UserViewSet

app_name = "user"

router = DefaultRouter()
router.register("", UserViewSet)
user_router = NestedSimpleRouter(router, "", lookup="user")
user_router.register("followers", UserViewSet, basename="followers")
user_router.register("following", UserViewSet, basename="following")
urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="logout"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("", include(router.urls)),
]
