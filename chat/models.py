from django.db import models
from skAuth.models import User

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.TextField()
    response = models.TextField()
    thinking_process = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Chat Histories"
    
    def __str__(self):
        return f"Chat {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
