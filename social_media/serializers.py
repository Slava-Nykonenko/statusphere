from django.db import transaction
from rest_framework import serializers

from social_media.models import Post, Hashtag, Comment


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("name",)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False, read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Post
        fields = ("id", "author", "content", "media_files", "shared_post", "hashtags")

    def create(self, validated_data):
        with transaction.atomic():
            hashtags = validated_data.pop("hashtags")
            post = Post.objects.create(**validated_data)
            for hashtag in hashtags:
                hashtag = Hashtag.objects.get_or_create(**hashtag)
                post.hashtags.add(hashtag)
            return post


class PostPreviewSerializer(PostSerializer):
    author = serializers.StringRelatedField(many=False, read_only=True)
    content_preview = serializers.SerializerMethodField(read_only=True)

    class Meta(PostSerializer.Meta):
        fields = ("author", "content_preview")

    @staticmethod
    def get_content_preview(post):
        output = {}
        if post.content:
            output["content"] = post.content
        if post.media_files:
            output["media_files"] = post.media_files[:250]
        return output


class PostListSerializer(PostSerializer):
    likes = serializers.IntegerField(read_only=True)
    shares = serializers.IntegerField(read_only=True)
    comments_num = serializers.IntegerField(read_only=True)
    hashtags = serializers.StringRelatedField(many=True, read_only=True)
    shared_post = PostPreviewSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        fields = (
            "author",
            "media_files",
            "shared_post",
            "hashtags",
            "likes",
            "shares",
            "comments_num",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "content", "media_files")


class CommentPostSerializer(CommentSerializer):
    author = serializers.StringRelatedField(many=False, read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + (
            "author",
            "created_at",
        )


class SharedPostSerializer(PostListSerializer):
    class Meta(PostSerializer.Meta):
        fields = ("id", "author", "content", "media_files", "created_at")


class RepostSerializer(PostListSerializer):
    class Meta:
        model = Post
        fields = ("id", "author")


class PostRetrieveSerializer(PostListSerializer):
    reactions = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="type"
    )
    comments = CommentPostSerializer(many=True, read_only=True)
    shared_post = SharedPostSerializer(many=False, read_only=True)
    reposts = RepostSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "author",
            "created_at",
            "content",
            "media_files",
            "shared_post",
            "hashtags",
            "likes",
            "reactions",
            "shares",
            "reposts",
            "comments_num",
            "comments",
        )
