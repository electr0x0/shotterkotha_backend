from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_with_ai, name='chat-with-ai'),
    path('chat/history/', views.get_chat_history, name='chat-history'),
] 