from re import findall

from django.db import transaction
from rest_framework import serializers

from social_media.models import Post, Hashtag, Comment, Reaction


class HashtagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)

    class Meta:
        model = Hashtag
        fields = ("name",)
        extra_kwargs = {"name": {"validators": []}}


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "content", "media_files", "shared_post")

    def create(self, validated_data):
        content = validated_data.get("content", "")
        extracted_tags = findall(r"#(\w+)", content)

        with transaction.atomic():
            post = Post.objects.create(**validated_data)
            for tag_name in extracted_tags:
                tag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
                post.hashtags.add(tag)
            return post


class PostListSerializer(PostSerializer):
    likes = serializers.IntegerField(read_only=True)
    shares = serializers.IntegerField(read_only=True)
    comments_num = serializers.IntegerField(read_only=True)
    hashtags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "media_files",
            "content_preview",
            "hashtags",
            "likes",
            "shares",
            "comments_num",
        )


class CommentSerializer(serializers.ModelSerializer):
    reactions = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = Comment
        fields = ("id", "content", "media_files", "reactions")


class CommentPostSerializer(CommentSerializer):
    author = serializers.StringRelatedField(many=False, read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ("author", "created_at")


class ReactionSerializer(serializers.ModelSerializer):
    object_id = serializers.IntegerField(write_only=True)
    object_type = serializers.CharField(write_only=True)

    class Meta:
        model = Reaction
        fields = ("type", "object_id", "object_type")


class ReactionPostSerializer(ReactionSerializer):
    author = serializers.StringRelatedField(many=False, read_only=True)

    class Meta(ReactionSerializer.Meta):
        fields = ("type", "author")


class SharedPostSerializer(PostListSerializer):
    class Meta(PostSerializer.Meta):
        fields = ("id", "author", "content", "media_files", "created_at")


class RepostSerializer(PostListSerializer):
    reposted_by = serializers.StringRelatedField(read_only=True, source="author")

    class Meta:
        model = Post
        fields = ("id", "reposted_by", "content")


class RepostMakeSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = ("content",)


class PostRetrieveSerializer(PostListSerializer):
    reactions = ReactionPostSerializer(many=True, read_only=True)
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
