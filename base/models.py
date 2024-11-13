from django.db import models
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission






# # Cre
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)




class CustomUser(AbstractUser):

   
    id = models.AutoField(primary_key=True, editable=False, default=None)
    email = models.EmailField(unique=True)
    objects = CustomUserManager()
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True)



    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }





# Create your models here.
class VideoAnalysis(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    video = models.FileField(upload_to='videos/')
    title = models.CharField(max_length=50, blank=True, null=True)
    analyzed_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    dominant_emotion = models.CharField(max_length=50, blank=True, null=True)
    calm_percentage = models.FloatField(blank=True, null=True)
    emotion_counts = models.JSONField(blank=True, null=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=True, null=True)  # Unique token field
    status = models.CharField(max_length=20, default='pending')
    
    def __str__(self):
        return f"{self.dominant_emotion} - {self.analyzed_on}"