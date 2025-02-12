from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from django.shortcuts import get_object_or_404

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        post = self.get_object()
        vote_type = request.data.get('vote_type')
        
        if vote_type not in ['up', 'down']:
            return Response(
                {'error': 'Invalid vote type'},
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
        
        return Response({'status': 'vote recorded'})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
