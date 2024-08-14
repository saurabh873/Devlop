from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from myapp import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('report/<int:file_id>/', views.generate_report, name='generate_report'),
    
    


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

