from django.contrib import admin
from .models import VideoAnalysis

@admin.register(VideoAnalysis)
class VideoAnalysisAdmin(admin.ModelAdmin):
    readonly_fields = ('dominant_emotion', 'analyzed_on', 'calm_percentage', 'emotion_counts', 'token', 'status')
    list_display = ('dominant_emotion', 'analyzed_on', 'status')

    def has_add_permission(self, request):
        return False  # Disable ability to add new instances

    def has_delete_permission(self, request, obj=None):
        return False  # Disable ability to delete instances
