from django.db import models
from skAuth.models import User
from django.core.validators import MinValueValidator
from .utils import process_media_file, generate_image_description

class Post(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    CATEGORY_CHOICES = [
        ('theft', 'Theft'),
        ('assault', 'Assault'),
        ('fraud', 'Fraud'),
        ('vandalism', 'Vandalism'),
        ('murder', 'Murder'),
        ('rape', 'Rape'),
        ('kidnapping', 'Kidnapping'),
        ('arson', 'Arson'),
        ('terrorism', 'Terrorism'),
        ('bribery', 'Bribery'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    fullAddress = models.CharField(max_length=255)
    crime_time = models.DateTimeField(null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    division = models.CharField(max_length=255, null=True, blank=True)
    
    # User can be null for anonymous posts
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Instead of ArrayField, we'll use ManyToManyField for votes
    upvotes = models.ManyToManyField(User, related_name='upvoted_posts', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_posts', blank=True)
    
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

class Media(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    post = models.ForeignKey(Post, related_name='media', on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_media/')
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    ai_description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    ai_analysis = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.pk:  # Only process on creation
            if self.file:
                processed_file, media_type = process_media_file(self.file)
                self.file = processed_file
                self.media_type = media_type
                
                # Generate AI analysis for images
                if media_type == 'image':
                    analysis = generate_image_description(self.file.path)
                    self.ai_analysis = analysis
                    self.ai_description = analysis.get('description', '')
                    
                    # Update post with AI-suggested severity and category
                    if self.post and analysis.get('isCrime', False):
                        self.post.severity = analysis.get('severity', 'low')
                        self.post.category = analysis.get('category', 'other')
                        self.post.save()
                    
        super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
