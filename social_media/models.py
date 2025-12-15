import pathlib
from uuid import uuid4

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext as _

from statusphere import settings


def user_media_files_path(instance: "Post" | "Comment", filename: str) -> pathlib.Path:
    model_name = instance.__class__.__name__.lower()
    unique_filename = f"{model_name}-{uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("uploads/media_files") / pathlib.Path(unique_filename)


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    media_files = models.FileField(
        upload_to=user_media_files_path, null=True, blank=True
    )
    shared_post = models.ForeignKey(
        "self",
        related_name="reposts",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    hashtags = models.ManyToManyField("Hashtag", blank=True, related_name="posts")
    reactions = GenericRelation("Reaction")

    def content_preview(self):
        output = self.content
        if len(output) > 250:
            output = output[:250] + "..."
        return output

    def shared_post_info(self):
        return {
            "post_id": self.id,
            "sharer": self.author.first_name + " " + self.author.last_name,
            "sharer_id": self.author.id,
        }


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    media_files = models.FileField(
        null=True, blank=True, upload_to=user_media_files_path
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    reactions = GenericRelation("Reaction")

    def __str__(self):
        return (
            f"{self.author.first_name} {self.author.last_name}: "
            f"{self.content[:50]}..."
        )


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "#" + self.name


class Reaction(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    REACTION_CHOICES = [
        ("LIKE", _("Like")),
        ("LOVE", _("Love")),
        ("HAHA", _("Haha")),
        ("WOW", _("Wow")),
        ("SAD", _("Sad")),
        ("ANGRY", _("Angry")),
    ]
    type = models.CharField(max_length=5, choices=REACTION_CHOICES, default="LIKE")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ["author", "content_type", "object_id"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return (
            f"{self.author.first_name} {self.author.last_name} reacted "
            f"{self.get_type_display()} on {self.content_type.model} "
            f"#{self.object_id}"
        )
