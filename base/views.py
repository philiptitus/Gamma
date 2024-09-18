import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VideoAnalysisSerializer
import cv2
from deepface import DeepFace
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .models import VideoAnalysis
from django.core.files.base import ContentFile
from threading import Thread

import logging



import threading
import logging
import uuid
from queue import Queue
import boto3
import io
import numpy as np
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import cv2
from deepface import DeepFace
from .models import VideoAnalysis
from django.conf import settings
from tempfile import NamedTemporaryFile

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
            video, token = task_queue.get()
            try:
                self.process_video(video, token)
            except Exception as e:
                logger.error(f"Error processing video: {e}")
            finally:
                task_queue.task_done()




    def process_video(self, video, token):
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
            result = self.analyze_video(temp_file_path)
            if not result:
                logger.error("No results from video analysis.")
                return

            # Update the VideoAnalysis instance with the analysis results
            video_analysis = VideoAnalysis.objects.get(token=token)
            video_analysis.dominant_emotion = result['dominant_emotion']
            video_analysis.calm_percentage = result['calm_percentage']
            video_analysis.emotion_counts = result['emotion_counts']
            video_analysis.save()
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            raise

    @transaction.atomic
    def post(self, request):
        video = request.FILES.get('video')
        if not video:
            return Response({"error": "No video provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate and send token before analysis
        token = self.generate_token()
        response_data = {"token": str(token)}
        response = Response(response_data, status=status.HTTP_200_OK)

        # Save initial VideoAnalysis object
        VideoAnalysis.objects.create(token=token)

        # Add the task to the queue
        task_queue.put((video, token))

        return response

    def analyze_video(self, temp_file_path):
        cap = cv2.VideoCapture(temp_file_path)
        frame_skip = 5
        resize_factor = 0.5

        total_frames = 0
        calm_frames = 0
        emotion_counts = {}
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False, detector_backend='mtcnn')

            for result in results:
                dominant_emotion = result['dominant_emotion']
                total_frames += 1
                if dominant_emotion in ['neutral', 'happy']:
                    calm_frames += 1

                emotion_counts.setdefault(dominant_emotion, 0)
                emotion_counts[dominant_emotion] += 1

        cap.release()
        cv2.destroyAllWindows()

        if total_frames == 0: 
            return None

        calm_percentage = (calm_frames / total_frames) * 100
        most_dominant_emotion = max(emotion_counts, key=emotion_counts.get)

        return {
            "dominant_emotion": most_dominant_emotion,
            "calm_percentage": calm_percentage,
            "emotion_counts": emotion_counts,
        }



# class AnalyzeVideoView(APIView):  
#     parser_classes = (MultiPartParser, FormParser)

#     def generate_token(self):
#         return uuid.uuid4()

#     def process_video(self, video, token):
#         # Create a temporary video file in the memory
#         temp_video_path = f'temp_{video.name}'
#         with open(temp_video_path, 'wb+') as temp_video:
#             for chunk in video.chunks():
#                 temp_video.write(chunk)

#         # Analyze the video
#         result = self.analyze_video(temp_video_path)
#         if not result:
#             # Log error if needed
#             return

#         # Create a ContentFile from the video content
#         with open(temp_video_path, 'rb') as temp_video:
#             video_content = ContentFile(temp_video.read())

#         # Create the VideoAnalysis instance
#         video_analysis = VideoAnalysis.objects.create(
#             video=video_content,
#             dominant_emotion=result['dominant_emotion'],
#             calm_percentage=result['calm_percentage'],
#             emotion_counts=result['emotion_counts'],
#             token=token
#         )

#         # Clean up the temporary video file
#         os.remove(temp_video_path)

#     @transaction.atomic
#     def post(self, request):
#         video = request.FILES.get('video')
#         if not video:
#             return Response({"error": "No video provided."}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate and send token before analysis
#         token = self.generate_token()
#         response_data = {"token": token}
#         response = Response(response_data, status=status.HTTP_200_OK)

#         # Process the video in a separate thread
#         thread = Thread(target=self.process_video, args=(video, token))
#         thread.start()

#         return response

#     def analyze_video(self, video_path):
#         cap = cv2.VideoCapture(video_path)
#         frame_skip = 5
#         resize_factor = 0.5

#         total_frames = 0
#         calm_frames = 0
#         emotion_counts = {}
#         frame_count = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame_count += 1
#             if frame_count % frame_skip != 0:
#                 continue

#             frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#             results = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False, detector_backend='mtcnn')

#             for result in results:
#                 dominant_emotion = result['dominant_emotion']
#                 total_frames += 1
#                 if dominant_emotion in ['neutral', 'happy']:
#                     calm_frames += 1

#                 emotion_counts.setdefault(dominant_emotion, 0)
#                 emotion_counts[dominant_emotion] += 1

#         cap.release()
#         cv2.destroyAllWindows()

#         if total_frames == 0:
#             return None

#         calm_percentage = (calm_frames / total_frames) * 100
#         most_dominant_emotion = max(emotion_counts, key=emotion_counts.get)

#         return {
#             "dominant_emotion": most_dominant_emotion,
#             "calm_percentage": calm_percentage,
#             "emotion_counts": emotion_counts,
#         }






# import threading
# import logging
# import os
# import uuid
# from queue import Queue
# from django.core.files.base import ContentFile
# from django.db import transaction
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import status
# import cv2
# from deepface import DeepFace
# from .models import VideoAnalysis

# logger = logging.getLogger(__name__)

# # Initialize a queue to hold video processing tasks
# task_queue = Queue()

# class AnalyzeVideoView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def __init__(self):
#         super().__init__()
#         self.worker_thread = threading.Thread(target=self.worker)
#         self.worker_thread.daemon = True
#         self.worker_thread.start()

#     def generate_token(self):
#         return uuid.uuid4()

#     def worker(self):
#         while True:
#             video, token = task_queue.get()
#             try:
#                 self.process_video(video, token)
#             except Exception as e:
#                 logger.error(f"Error processing video: {e}")
#             finally:
#                 task_queue.task_done()

#     def process_video(self, video, token):
#         try:
#             # Create a temporary video file in the memory
#             temp_video_path = f'temp_{video.name}'
#             with open(temp_video_path, 'wb+') as temp_video:
#                 for chunk in video.chunks():
#                     temp_video.write(chunk)

#             # Analyze the video
#             result = self.analyze_video(temp_video_path)
#             if not result:
#                 # Log error if needed
#                 logger.error("No results from video analysis.")
#                 return

#             # Create a ContentFile from the video content
#             with open(temp_video_path, 'rb') as temp_video:
#                 video_content = ContentFile(temp_video.read())

#             # Create the VideoAnalysis instance
#             video_analysis = VideoAnalysis.objects.get(token=token)
#             video_analysis.dominant_emotion = result['dominant_emotion']
#             video_analysis.calm_percentage = result['calm_percentage']
#             video_analysis.emotion_counts = result['emotion_counts']
#             video_analysis.video.save(f"{token}.mp4", video_content)
#             video_analysis.save()

#             # Clean up the temporary video file
#             os.remove(temp_video_path)
#         except Exception as e:
#             logger.error(f"Error processing video: {e}")
#             raise

#     @transaction.atomic
#     def post(self, request):
#         video = request.FILES.get('video')
#         if not video:
#             return Response({"error": "No video provided."}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate and send token before analysis
#         token = self.generate_token()
#         response_data = {"token": str(token)}
#         response = Response(response_data, status=status.HTTP_200_OK)

#         # Save initial VideoAnalysis object
#         VideoAnalysis.objects.create(token=token) 

#         # Add the task to the queue
#         task_queue.put((video, token))

#         return response

#     def analyze_video(self, video_path):
#         cap = cv2.VideoCapture(video_path)
#         frame_skip = 5
#         resize_factor = 0.5

#         total_frames = 0
#         calm_frames = 0
#         emotion_counts = {}
#         frame_count = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame_count += 1
#             if frame_count % frame_skip != 0:
#                 continue

#             frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#             results = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False, detector_backend='mtcnn')

#             for result in results:
#                 dominant_emotion = result['dominant_emotion']
#                 total_frames += 1
#                 if dominant_emotion in ['neutral', 'happy']:
#                     calm_frames += 1

#                 emotion_counts.setdefault(dominant_emotion, 0)
#                 emotion_counts[dominant_emotion] += 1

#         cap.release()
#         cv2.destroyAllWindows()

#         if total_frames == 0:
#             return None

#         calm_percentage = (calm_frames / total_frames) * 100
#         most_dominant_emotion = max(emotion_counts, key=emotion_counts.get)

#         return {
#             "dominant_emotion": most_dominant_emotion,
#             "calm_percentage": calm_percentage,
#             "emotion_counts": emotion_counts,
#         }





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




