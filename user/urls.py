from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from user.views import CreateTokenView, CreateUserView, UserViewSet

app_name = "user"

router = DefaultRouter()
router.register("", UserViewSet)
user_router = NestedSimpleRouter(router, "", lookup="user")
user_router.register("followers", UserViewSet, basename="followers")
user_router.register("following", UserViewSet, basename="following")
urlpatterns = [
    path("token/", CreateTokenView.as_view(), name="token"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("", include(router.urls)),
]
