from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, generics, authentication, permissions


from core.models import AudioFile
from .serializers import AudioFileSerializer
from .utils import calculate_speed_of_sound, convert_speed_to_mph

import logging

logger = logging.getLogger(__name__)


class AudioFileListView(generics.ListCreateAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    pagination_class = LimitOffsetPagination
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return AudioFile.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Get the queryset
        queryset = self.get_queryset()
        audio_files_data = []

        for instance in queryset:
            serializer = self.get_serializer(instance)

            speed, speed_unit, peaks = calculate_speed_of_sound(
                float(instance.distance), instance.file.path, instance.unit
            )

            audio_files_data.append(
                {
                    **serializer.data,
                    "speed": speed,
                    "speed_unit": speed_unit,
                    "peaks": peaks,
                }
            )

        # logger.info(f"audio_files_data :  {audio_files_data}")

        return Response(audio_files_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        distance = request.data.get("distance", 0)
        unit = request.data.get("unit", "inches")
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            audio_file_path = serializer.instance.file.path
            speed, speed_unit, peaks = calculate_speed_of_sound(
                float(distance), audio_file_path, unit
            )
            return Response(
                {
                    **serializer.data,
                    "speed": speed,
                    "speed_unit": speed_unit,
                    "peaks": peaks,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    lookup_field = "id"
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.file.delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def calculate_and_respond(self, instance, serializer_data, unit=None):
        """Helper function to calculate speed and peaks and format the response."""
        distance = instance.distance
        audio_file_path = instance.file.path

        unit = unit or instance.unit
        speed, speed_unit, peaks = calculate_speed_of_sound(
            float(distance), audio_file_path, unit
        )

        return Response(
            {
                **serializer_data,
                "speed": speed,
                "speed_unit": speed_unit,
                "peaks": peaks,
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return self.calculate_and_respond(instance, serializer.data)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            unit = request.data.get("unit", instance.unit)
            return self.calculate_and_respond(instance, serializer.data, unit=unit)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            unit = request.data.get("unit", instance.unit)
            return self.calculate_and_respond(instance, serializer.data, unit=unit)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        # Get the user's audio files
        audio_files = AudioFile.objects.filter(user=request.user)
        audio_statistics = []
        all_speeds = []

        for audio_file in audio_files:
            speed, speed_unit, peaks = calculate_speed_of_sound(
                float(audio_file.distance), audio_file.file.path, audio_file.unit
            )

            # Convert speed to MPH
            speed_mph = convert_speed_to_mph(speed, audio_file.unit)
            all_speeds.append(speed_mph)

            audio_statistics.append(
                {
                    "file_name": audio_file.file.name,
                    "speed": speed_mph,
                    "speed_unit": "MPH",  # Update unit to MPH
                    "peaks": peaks,
                    "distance": audio_file.distance,
                    "unit": audio_file.unit,
                }
            )

        # Calculate min, max, and average speeds
        min_speed = min(all_speeds) if all_speeds else 0
        max_speed = max(all_speeds) if all_speeds else 0
        avg_speed = sum(all_speeds) / len(all_speeds) if all_speeds else 0

        response_data = {
            "audio_statistics": audio_statistics,
            "min_speed": min_speed,
            "max_speed": max_speed,
            "avg_speed": avg_speed,
            "all_speeds": all_speeds,
        }

        return Response(response_data, status=status.HTTP_200_OK)
