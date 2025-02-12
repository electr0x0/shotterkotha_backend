from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # The public-posts endpoint will be automatically included by the router
    # It will be available at: /posts/public_posts/
] 