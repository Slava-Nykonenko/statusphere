from celery import shared_task
from django.core.management import call_command

from .models import Post


@shared_task
def publish_scheduled_post(post_id: int) -> str:
    try:
        post = Post.objects.get(pk=post_id)
        post.published = True
        post.save()
        return f"Post {post_id} published successfully."
    except Post.DoesNotExist:
        return f"Post {post_id} not found."


@shared_task
def flush_expired_tokens():
    call_command("flushexpiredtokens")
    return "Expired tokens flushed successfully."
