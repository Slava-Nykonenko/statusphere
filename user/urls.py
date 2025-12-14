from django.urls import path
from user.views import (
    CreateTokenView,
    CreateUserView,
    UserViewSet
)

app_name = "user"

urlpatterns = [
    path("user/token/", CreateTokenView.as_view(), name="token"),
    path("user/register/", CreateUserView.as_view(), name="register"),
    path("user/<int:pk>/", UserViewSet.as_view(), name="user"),
]
