from django.urls import path
from .views import AudioFileListView, AudioFileDetailView

app_name = 'audio'


urlpatterns = [
    path("audio-files/", AudioFileListView.as_view(), name="audiofile-list-create"),
    path(
        "audio-files/<int:id>/", AudioFileDetailView.as_view(), name="audiofile-detail"
    ),
]
