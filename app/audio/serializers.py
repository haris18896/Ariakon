from rest_framework import serializers
from core.models import AudioFile


class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ["id", "file", "unit", "distance", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        return AudioFile.objects.create(**validated_data)

    def validate_distance(self, value):
        if value <= 0:
            raise serializers.ValidationError("Distance must be greater than zero.")
        return value

    def validate_file(self, value):
        if not value.name.endswith(('.wav', '.mp3', '.flac')):
            raise serializers.ValidationError("File type not supported.")
        return value
