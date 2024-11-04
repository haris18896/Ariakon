from django.urls import path
from .views import AudioFileListView, AudioFileDetailView, AudioStatisticsView

app_name = "audio"


urlpatterns = [
    path("audio-files/", AudioFileListView.as_view(), name="audiofile-list-create"),
    path(
        "audio-files/<int:id>/", AudioFileDetailView.as_view(), name="audiofile-detail"
    ),
    path('audio-statistics/', AudioStatisticsView.as_view(), name='audio-statistics'),  # New endpoint
]
