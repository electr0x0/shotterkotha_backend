from rest_framework import serializers
from .models import Post, Media, Comment
from skAuth.serializers import UserSerializer
from .utils import generate_image_description
import json
from django.utils import timezone
from datetime import datetime

class MediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = [
            'id', 
            'file', 
            'file_url', 
            'media_type', 
            'order', 
            'ai_description', 
            'ai_analysis'
        ]
        
    def get_file_url(self, obj):
        if obj.file:
            try:
                return obj.file.url
            except Exception:
                return None
        return None

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)
    media_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    user = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    upvotes_count = serializers.SerializerMethodField()
    downvotes_count = serializers.SerializerMethodField()
    has_user_voted = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    description = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 
            'title', 
            'description', 
            'fullAddress', 
            'severity',
            'category', 
            'user', 
            'media', 
            'media_files',
            'upvotes_count', 
            'downvotes_count', 
            'comments_count',
            'has_user_voted', 
            'created_at', 
            'time_ago', 
            'latitude',
            'longitude', 
            'is_verified', 
            'is_approved', 
            'crime_time',
            'district', 
            'division'
        ]
        read_only_fields = ['is_verified', 'is_approved']

    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        if not isinstance(media_files, list):
            media_files = [media_files]

        post = Post.objects.create(**validated_data)
        
        for index, file in enumerate(media_files):
            media_type = 'image' if file.content_type.startswith('image/') else 'video'
            media_obj = Media.objects.create(
                post=post,
                file=file,
                media_type=media_type,
                order=index
            )
            
            if media_type == 'image':
                try:
                    analysis = generate_image_description(media_obj.file.path)
                    media_obj.ai_analysis = analysis
                    media_obj.ai_description = analysis.get('description', '')
                    media_obj.save()
                    
                    # Update post description if it's empty
                    if not validated_data.get('description'):
                        post.description = analysis.get('description', '')
                        post.save()
                        
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue
        
        return post

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_upvotes_count(self, obj):
        return obj.upvotes.count()

    def get_downvotes_count(self, obj):
        return obj.downvotes.count()

    def get_has_user_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.upvotes.filter(id=request.user.id).exists():
                return "up"
            elif obj.downvotes.filter(id=request.user.id).exists():
                return "down"
        return None

    def get_time_ago(self, obj):
        now = timezone.now()
        time_difference = now - obj.created_at
        
        days = time_difference.days
        hours = time_difference.seconds // 3600
        minutes = (time_difference.seconds % 3600) // 60
        
        if days > 365:
            years = days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
        elif days > 30:
            months = days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        elif days > 0:
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now" 