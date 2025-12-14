from django.db import transaction
from rest_framework import serializers

from social_media.models import Post, Hashtag


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("name",)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False, read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=False)

    class Meta:
        model = Post
        fields = ("id", "author", "content", "media_files", "hashtags")

    def create(self, validated_data):
        with transaction.atomic():
            hashtags = validated_data.pop("hashtags")
            post = Post.objects.create(**validated_data)
            for hashtag in hashtags:
                hashtag = Hashtag.objects.create(**hashtag)
                post.hashtags.add(hashtag)
            return post


class PostListSerializer(PostSerializer):
    likes = serializers.IntegerField(read_only=True)
    shares = serializers.IntegerField(read_only=True)
    comments_num = serializers.IntegerField(read_only=True)
    hashtags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "author",
            "content_preview",
            "media_files",
            "hashtags",
            "likes",
            "shares",
            "comments_num",
        )


class PostRetrieveSerializer(PostListSerializer):

    class Meta:
        model = Post
        fields = (
            "author",
            "created_at",
            "content",
            "media_files",
            "hashtags",
            "likes",
            "shares",
            "comments_num",
            "comments",
        )
