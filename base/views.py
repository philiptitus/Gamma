import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VideoAnalysisSerializer
import cv2
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .models import VideoAnalysis
from django.core.files.base import ContentFile
from threading import Thread
from django.contrib.auth.password_validation import validate_password
from rest_framework.decorators import permission_classes
from django.contrib.auth.hashers import make_password

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
from django.db import IntegrityError
from django.core.validators import *



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
    permission_classes = [IsAuthenticated]
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
            video, token, email, user = task_queue.get()
            try:
                self.process_video(video, token, email, user)
            except Exception as e:
                logger.error(f"Error processing video: {e}")
            finally:
                task_queue.task_done()

    def process_video(self, video, token, email, user):
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
            video_analysis.user = user
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
        if not video:
            return Response({"error": "No video provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch email from request.user
        email = request.user.email

        # Generate and send token before analysis
        token = self.generate_token()
        response_data = {"token": str(token)}
        response = Response(response_data, status=status.HTTP_200_OK)

        # Save initial VideoAnalysis object
        video_analysis = VideoAnalysis.objects.create(token=token, user=request.user)

        # Add the task to the queue
        task_queue.put((video, token, email, request.user))

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
from .models import *
from .serializers import *






class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
       def validate(self, attrs: dict[str, any]) -> dict[str, str]:
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v



        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q







from django.db.models import Case, When, Value, IntegerField

from django.db.models import Q, F
from rest_framework.pagination import PageNumberPagination

from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Q
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.



class MyLoginView(TokenObtainPairView):
        serializer_class = MyTokenObtainPairSerializer

        # No need for JWT authentication logic here
        # No need to generate JWT token or expiration time

        # Return the default response provided by the parent class





class RegisterUser(APIView):

    def post(self, request):
        data = request.data

        print("Data received from the form:", data)


        template_path = os.path.join(settings.BASE_DIR, 'base/email_templates', 'Register.html')

        try:
            with open(template_path, 'r', encoding='utf-8') as template_file:
                email_content = template_file.read()
        except FileNotFoundError:
            return Response({'detail': 'Email template not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Define required fields based on user type
        fields_to_check = ['name', 'email', 'password']

        # Check if all required fields are present
        for field in fields_to_check:
            if field not in data:
                return Response({'detail': f'Missing {field} field.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check password length
        if len(data['password']) < 8:
            return Response({'detail': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check password for username and email
        if data['password'].lower() in [data['name'].lower(), data['email'].lower()]:
            return Response({'detail': 'Password cannot contain username or email.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(data['email'])
        except:
            return Response({'detail': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password strength
        try:
            validate_password(data['password'])
        except:
            return Response({'detail': 'Password must meet complexity requirements.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        try:
            user = CustomUser.objects.create_user(
                first_name=data['name'],
                username=data['email'],
                email=data['email'],
                password=data['password'],
            )



            user.save()

            abslink = "http://localhost:3000/#/forgot-password/"
            email_subject = "Welcome to RE-UP"
            to_email = user.email
            email_data = {
                'email_body': email_content,
                'email_subject': email_subject,
                'to_email': to_email,
                'context': {
                    'link': abslink,
                },
            }
            send_normal_email(email_data)

        except IntegrityError:
            return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)











@permission_classes([IsAuthenticated])
class GetUserProfile(APIView):

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, many=False)




        return Response(serializer.data)

class UpdateUserProfile(APIView):

    def put(self, request):
        user = request.user
        serializer = UserSerializerWithToken(user, many=False)
        data = request.data

        new_email = data.get('email')

        # Check if email is being updated to an existing email
        if new_email and CustomUser.objects.exclude(pk=user.pk).filter(email=new_email).exists():
            return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update password if provided
        if 'password' in data and data['password'] != '':
            # Add password strength checks here
            if len(data['password']) < 8:
                content = {'detail': 'Password must be at least 8 characters long.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            uppercase_count = sum(1 for c in data['password'] if c.isupper())
            lowercase_count = sum(1 for c in data['password'] if c.islower())
            if uppercase_count < 1 or lowercase_count < 1:
                content = {'detail': 'Password must contain at least one uppercase and lowercase character.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            digit_count = sum(1 for c in data['password'] if c.isdigit())
            special_count = sum(1 for c in data['password'] if not c.isalnum())
            if digit_count < 1 or special_count < 1:
                content = {'detail': 'Password must contain at least one digit and one special character.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            user.password = make_password(data['password'])

        # Update user profile details
        user.first_name = data.get('name', user.first_name)
        user.username = data.get('email', user.username)
        user.email = data.get('email', user.email)

        # Save updated user profile
        user.save()

        # Return updated user data
        return Response(serializer.data)
from rest_framework.exceptions import PermissionDenied



@permission_classes([IsAuthenticated])
class deleteAccount(APIView):

    def delete(self, request):
        user_for_deletion = request.user
        user_for_deletion.delete()
        return Response({"detail": "Account deleted successfully."}, status=status.HTTP_200_OK)







class GetAnalysisResultView(APIView):
    permission_classes = [IsAuthenticated]

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
