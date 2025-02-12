from django.contrib import admin
from .models import ChatHistory

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'prompt', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('prompt', 'response', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
