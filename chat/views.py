from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import ChatHistory
from .utils import get_groq_response

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_ai(request):
    """
    API endpoint for chatting with the AI and saving chat history
    """
    try:
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {"error": "Prompt is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get AI response
        thinking, response = get_groq_response(prompt)

        # Save chat history
        chat_history = ChatHistory.objects.create(
            user=request.user if request.user.is_authenticated else None,
            prompt=prompt,
            response=response,
            thinking_process=thinking
        )

        return Response({
            "thinking": thinking,
            "response": response,
            "chat_id": chat_history.id,
            "created_at": chat_history.created_at
        })

    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_chat_history(request):
    """
    Get chat history for the current user or all chats if user is admin
    """
    try:
        if request.user.is_authenticated:
            if request.user.is_staff:
                # Admin can see all chats
                chats = ChatHistory.objects.all()
            else:
                # Regular users see their own chats
                chats = ChatHistory.objects.filter(user=request.user)
            
            chat_data = [{
                "id": chat.id,
                "prompt": chat.prompt,
                "response": chat.response,
                "thinking_process": chat.thinking_process,
                "created_at": chat.created_at,
                "user": chat.user.username if chat.user else "Anonymous"
            } for chat in chats]

            return Response(chat_data)
        else:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
