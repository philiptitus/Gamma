from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
import json 
from .models import CustomUser

from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import *
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
import jwt
from pytz import timezone  # Import timezone from pytz
from datetime import timedelta
from datetime import datetime




class VideoAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAnalysis
        fields = '__all__'






class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)








    class Meta:
        model = CustomUser
        fields = '__all__'



    def get__id(self, obj):
        return obj.id

    

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email

        return name




class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    expiration_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', '_id', 'username', 'email', 'name','token', 'expiration_time']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        print("Your Token is:", token)

        return str(token.access_token)

    def get_expiration_time(self, obj):
        token = RefreshToken.for_user(obj)
        access_token = str(token.access_token)
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})  # Decode token without verification
        expiration_timestamp = decoded_token['exp']  # Get the expiration time from the decoded token
        expiration_datetime_utc = datetime.utcfromtimestamp(expiration_timestamp)  # Convert expiration timestamp to UTC datetime
        expiration_datetime_local = expiration_datetime_utc.astimezone(timezone('Africa/Nairobi'))  # Convert to Nairobi timezone
        expiration_datetime_local += timedelta(hours=3)  # Add three hours to the expiration time
        return expiration_datetime_local.strftime('%Y-%m-%d %H:%M:%S %Z')  #



