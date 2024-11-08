from django.contrib import admin
from django.urls import *
from django.conf import settings
from django.conf.urls.static import static
from base.views import *

urlpatterns = [
    path('', landing_page, name='landing-page'),
    path('api/v1/', include('base.urls')),
    path('admin/', admin.site.urls),

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
