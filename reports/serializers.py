from rest_framework import serializers
from .models import Post, Media, Comment
from skAuth.serializers import UserSerializer
from .utils import generate_image_description
import json

class MediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = ['id', 'file_url', 'media_type', 'ai_description', 'order']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)
    media_upload = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
        source='media'
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
            'id', 'title', 'description', 'fullAddress', 'severity',
            'category', 'user', 'media', 'media_upload', 'comments', 
            'upvotes_count', 'downvotes_count', 'comments_count', 
            'has_user_voted', 'created_at', 'time_ago', 'latitude', 
            'longitude', 'is_verified', 'is_approved', 'crime_time', 
            'district', 'division'
        ]
        read_only_fields = ['is_verified', 'is_approved', 'description']

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
                return 'up'
            elif obj.downvotes.filter(id=request.user.id).exists():
                return 'down'
        return None

    def get_time_ago(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(obj.created_at, timezone.now())

    def create(self, validated_data):
        media_files = validated_data.pop('media')
        post = Post.objects.create(**validated_data)
        
        has_valid_crime_media = False
        ai_description = None
        
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
                    
                    if analysis.get('isCrime', False) and not ai_description:
                        ai_description = analysis.get('description', '')
                    
                    if analysis.get('isCrime', False):
                        has_valid_crime_media = True
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue
        
        if ai_description:
            post.description = ai_description
            post.save()
        
        if not has_valid_crime_media:
            post.delete()
            raise serializers.ValidationError(
                "No valid crime-related content detected in the uploaded media."
            )
        
        return post 