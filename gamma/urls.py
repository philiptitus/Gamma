from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from base.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('analyze/', AnalyzeVideoView.as_view(), name='analyze-video'),

    path('get/<uuid:token>/', GetAnalysisResultView.as_view(), name='get_analysis_result'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
