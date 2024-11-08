from django.urls import path, include
from .views import *


urlpatterns = [

   

    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('profile/', GetUserProfile.as_view(), name='user-profile'),
    path('delete/', deleteAccount.as_view(), name='delete'),
    path('profile/update/', UpdateUserProfile.as_view(), name='user-profile-update'),
    path('analyze/', AnalyzeVideoView.as_view(), name='analyze-video'),
    path('get/<uuid:token>/', GetAnalysisResultView.as_view(), name='get_analysis_result'),
]
