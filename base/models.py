from django.db import models
import uuid


# Create your models here.
class VideoAnalysis(models.Model):
    video = models.FileField(upload_to='videos/')
    analyzed_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    dominant_emotion = models.CharField(max_length=50, blank=True, null=True)
    calm_percentage = models.FloatField(blank=True, null=True)
    emotion_counts = models.JSONField(blank=True, null=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=True, null=True)  # Unique token field
    status = models.CharField(max_length=20, default='pending')
    
    def __str__(self):
        return f"{self.dominant_emotion} - {self.analyzed_on}"