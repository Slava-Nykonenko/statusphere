import pathlib
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models


def user_media_files_path(
        instance: "Post" | "Comment",
        filename: str) -> pathlib.Path:
    model_name = instance.__class__.__name__.lower()
    unique_filename = f"{model_name}-{uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("uploads/media_files") / pathlib.Path(unique_filename)


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    media_files = models.FileField(
        upload_to=user_media_files_path,
        null=True,
        blank=True
    )
    shared_post = models.ForeignKey(
        "self",
        related_name="child_posts",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    hashtags = models.ManyToManyField(
        "Hashtag",
        blank=True,
        related_name="posts"
    )
    liked_by = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name="liked_post",
        symmetrical=False
    )
    shared_by = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name="parent_post",
        symmetrical=False
    )


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    media_files = models.FileField(
        null=True,
        blank=True,
        upload_to=user_media_files_path
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.author.first_name} {self.author.last_name}: "
            f"{self.content[:50]}..."
        )


class Hashtag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return "#" + self.name
