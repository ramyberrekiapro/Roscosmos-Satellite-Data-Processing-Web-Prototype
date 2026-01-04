from django.urls import path
from . import views

app_name = 'files'  # This is your namespace

urlpatterns = [
    path('upload/', views.upload_files, name='upload'),
    path('convert/', views.convert, name='convert'),
    path('howto/', views.howto_view, name='howto'),
]
