from rest_framework import serializers
from .models import Post, Media, Comment
from skAuth.serializers import UserSerializer

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'media_type', 'ai_description', 'order']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, required=True)
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    upvotes_count = serializers.SerializerMethodField()
    downvotes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    has_user_voted = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'description', 'location', 'severity',
            'category', 'user', 'media', 'comments', 'upvotes_count',
            'downvotes_count', 'comments_count', 'has_user_voted',
            'created_at', 'time_ago', 'latitude', 'longitude',
            'is_verified', 'is_approved'
        ]
        read_only_fields = ['is_verified', 'is_approved']

    def get_upvotes_count(self, obj):
        return obj.upvotes.count()

    def get_downvotes_count(self, obj):
        return obj.downvotes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return 'just now'
        elif diff < timedelta(hours=1):
            return f'{int(diff.seconds/60)} minutes ago'
        elif diff < timedelta(days=1):
            return f'{int(diff.seconds/3600)} hours ago'
        else:
            return f'{diff.days} days ago'

    def get_has_user_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.upvotes.filter(id=request.user.id).exists():
                return 'up'
            elif obj.downvotes.filter(id=request.user.id).exists():
                return 'down'
        return None

    def validate(self, data):
        if 'media' not in data or not data['media']:
            raise serializers.ValidationError(
                "At least one image or video is required"
            )
        return data

    def create(self, validated_data):
        media_data = validated_data.pop('media')
        post = Post.objects.create(**validated_data)
        
        for media in media_data:
            media_obj = Media.objects.create(post=post, **media)
            if media_obj.media_type == 'image':
                # Generate AI description
                from .utils import generate_image_description
                media_obj.ai_description = generate_image_description(media_obj.file.path)
                media_obj.save()
        
        # Validate post using custom util
        from .utils import isValidCrimePost
        if not isValidCrimePost(post):
            post.delete()
            raise serializers.ValidationError(
                "Post validation failed. It may not be a valid crime report."
            )
        
        return post 