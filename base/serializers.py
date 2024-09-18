from rest_framework import serializers
from .models import VideoAnalysis

class VideoAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAnalysis
        fields = '__all__'
