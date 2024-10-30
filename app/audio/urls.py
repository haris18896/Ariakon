from django.urls import path
from . import views

app_name = "audio"

urlpatterns = [
    # # URL to upload an audio file
    # path('upload/', views.upload_audio, name='upload_audio'),
    #
    # # URL to retrieve a list of audio files
    # path('files/', views.list_audio_files, name='list_audio_files'),
    #
    # # URL to retrieve a specific audio file's details
    # path('files/<int:audio_id>/', views.audio_detail, name='audio_detail'),
    #
    # # URL to delete a specific audio file
    # path('files/<int:audio_id>/delete/', views.delete_audio, name='delete_audio'),
    #
    # # URL to play a specific audio file
    # path('files/<int:audio_id>/play/', views.play_audio, name='play_audio'),
    #
    # # URL to get audio waveform data (if applicable)
    # path('files/<int:audio_id>/waveform/', views.audio_waveform, name='audio_waveform'),
]
