from typing import Any, Generator

from celery import shared_task
from django.core.management import call_command
from django.utils import timezone

from .models import Post


@shared_task
def publish_scheduled_post() -> str:
    Post.objects.filter(scheduled_at__lte=timezone.now(), published=False).update(
        published=True
    )
    return "Scheduled tasks have been published."


@shared_task
def flush_expired_tokens():
    call_command("flushexpiredtokens")
    return "Expired tokens flushed successfully."
