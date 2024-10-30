from rest_framework import serializers
from core.models import AudioFile


class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ["id", "user", "file", "distance", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
