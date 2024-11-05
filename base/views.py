import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VideoAnalysisSerializer
import cv2
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .models import VideoAnalysis
from django.core.files.base import ContentFile
from threading import Thread

import logging
import threading
import uuid
from queue import Queue
import boto3
import io
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from tempfile import NamedTemporaryFile
from .utils import analyze_video,send_normal_email

logger = logging.getLogger(__name__)

# Initialize a queue to hold video processing tasks
task_queue = Queue()

# Initialize the S3 client with explicit credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)


class AnalyzeVideoView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def __init__(self):
        super().__init__()
        self.worker_thread = threading.Thread(target=self.worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def generate_token(self):
        return uuid.uuid4()

    def worker(self):
        while True:
            video, token, email = task_queue.get()
            try:
                self.process_video(video, token, email)
            except Exception as e:
                logger.error(f"Error processing video: {e}")
            finally:
                task_queue.task_done()

    def process_video(self, video, token, email):
        try:
            AWS_S3_CUSTOM_DOMAIN = settings.AWS_S3_CUSTOM_DOMAIN

            # Create a file-like object for the uploaded video
            video_io = io.BytesIO()
            for chunk in video.chunks():
                video_io.write(chunk)
            video_io.seek(0)

            # Upload the video to S3
            temp_video_key = f'temp_{uuid.uuid4()}_{video.name}'
            s3_client.upload_fileobj(video_io, settings.AWS_STORAGE_BUCKET_NAME, temp_video_key)

            # Stream the video for analysis directly from S3
            temp_video_obj = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=temp_video_key)
            temp_video_stream = io.BytesIO(temp_video_obj['Body'].read())

            # Save the video stream to a temporary file for OpenCV
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(temp_video_stream.read())
                temp_file_path = temp_file.name

            # Analyze the video
            result = analyze_video(temp_file_path)
            if not result:
                logger.error("No results from video analysis.")
                return

            # Update the VideoAnalysis instance with the analysis results
            video_analysis = VideoAnalysis.objects.get(token=token)
            video_analysis.dominant_emotion = result['dominant_emotion']
            video_analysis.calm_percentage = result['calm_percentage']
            video_analysis.emotion_counts = result['emotion_counts']
            video_analysis.save()

            template_path = os.path.join(settings.BASE_DIR, 'base/email_templates', 'Gamma.html')
            with open(template_path, 'r', encoding='utf-8') as template_file:
                html_content = template_file.read()

            email_data = {
                'email_subject': 'Your Screening Session Results',
                'email_body': html_content,
                'to_email': email,
                'context': {
                    'calm': video_analysis.calm_percentage,
                    'dominant': video_analysis.dominant_emotion
                },
            }
            send_normal_email(email_data)
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            raise

    @transaction.atomic
    def post(self, request):
        video = request.FILES.get('video')
        email = request.data.get('email')
        if not video:
            return Response({"error": "No video provided."}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "No email provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate and send token before analysis
        token = self.generate_token()
        response_data = {"token": str(token)}
        response = Response(response_data, status=status.HTTP_200_OK)

        # Save initial VideoAnalysis object
        VideoAnalysis.objects.create(token=token)

        # Add the task to the queue
        task_queue.put((video, token, email))

        return response
    


# views.py
import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VideoAnalysisSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .models import VideoAnalysis
from django.core.files.base import ContentFile
# myapp/tasks.py



# views.py
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)








# views.py
# views.py

import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import VideoAnalysis

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import VideoAnalysis
from .serializers import VideoAnalysisSerializer

class GetAnalysisResultView(APIView):
    def get(self, request, token):
        try:
            video_analysis = VideoAnalysis.objects.get(token=token)
            if video_analysis.calm_percentage is None:
                return Response({"message": "Your analysis is not done yet. Please be patient, it will be ready soon."}, status=status.HTTP_200_OK)
            
            serializer = VideoAnalysisSerializer(video_analysis)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except VideoAnalysis.DoesNotExist:
            return Response({"error": "No analysis found for this token."}, status=status.HTTP_404_NOT_FOUND)




from django.shortcuts import render

def landing_page(request):
    return render(request, 'landing.html')
