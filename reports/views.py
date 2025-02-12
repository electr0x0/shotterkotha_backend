from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# Create your views here.

@authentication_classes([JWTAuthentication])  # Add JWT authentication
@permission_classes([permissions.AllowAny])  # Allow any user
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_permissions(self):
        """
        - List and Retrieve actions are allowed for anyone
        - Vote requires authentication
        - Create is allowed for authenticated users
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        List all posts without authentication
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific post without authentication
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Handle the media file from request.FILES
        media_file = request.FILES.get('media')
        
        # Create mutable copy of data
        mutable_data = request.data.copy()
        
        # Add media_files to the data
        if media_file:
            mutable_data.setlist('media_files', [media_file])
        
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        post = self.get_object()
        vote_type = request.data.get('vote_type')

        if vote_type not in ['up', 'down']:
            return Response(
                {'error': 'Invalid vote type. Must be "up" or "down".'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove existing votes
        post.upvotes.remove(request.user)
        post.downvotes.remove(request.user)

        # Add new vote
        if vote_type == 'up':
            post.upvotes.add(request.user)
        else:
            post.downvotes.add(request.user)

        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        """
        Get heatmap data with filters for time range and crime type
        """
        # Get query parameters
        time_range = request.query_params.get('time_range', '30d')
        crime_type = request.query_params.get('crime_type', 'all')
        
        # Calculate the date range
        now = timezone.now()
        if time_range == '24h':
            start_date = now - timedelta(days=1)
        elif time_range == '7d':
            start_date = now - timedelta(days=7)
        elif time_range == '30d':
            start_date = now - timedelta(days=30)
        elif time_range == '90d':
            start_date = now - timedelta(days=90)
        elif time_range == '1y':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)  # Default to 30 days

        # Base queryset
        queryset = Post.objects.filter(
            created_at__gte=start_date,
            latitude__isnull=False,
            longitude__isnull=False
        )

        # Filter by crime type if specified
        if crime_type != 'all':
            queryset = queryset.filter(category=crime_type)

        # Aggregate data points
        posts = queryset.values('latitude', 'longitude', 'category', 'severity')
        
        # Calculate weights based on severity and aggregate counts
        heatmap_data = []
        for post in posts:
            # Convert severity to weight
            weight = {
                'high': 1.0,
                'medium': 0.7,
                'low': 0.4
            }.get(post['severity'], 0.5)

            heatmap_data.append({
                'lat': float(post['latitude']),
                'lng': float(post['longitude']),
                'weight': weight,
                'category': post['category'],
                'name': post.get('district', 'Unknown Location'),
                'crimes': 1  # Each post represents one crime
            })

        # Aggregate points at same location
        aggregated_data = {}
        for point in heatmap_data:
            key = f"{point['lat']},{point['lng']}"
            if key in aggregated_data:
                aggregated_data[key]['crimes'] += 1
                aggregated_data[key]['weight'] = min(1.0, aggregated_data[key]['weight'] + 0.1)
            else:
                aggregated_data[key] = point

        response_data = {
            'points': list(aggregated_data.values()),
            'metadata': {
                'total_crimes': len(posts),
                'time_range': time_range,
                'crime_type': crime_type,
                'date_from': start_date.isoformat(),
                'date_to': now.isoformat()
            }
        }

        return Response(response_data)
