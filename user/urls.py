from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import CreateTokenView, CreateUserView, UserViewSet

app_name = "user"

router = DefaultRouter()
router.register("", UserViewSet)
urlpatterns = [
    path("token/", CreateTokenView.as_view(), name="token"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("", include(router.urls)),
]
