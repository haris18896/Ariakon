from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, generics, authentication, permissions
from core.models import AudioFile
from .serializers import AudioFileSerializer
from .utils import calculate_speed_of_sound, validate_audio_file
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
        """Get queryset filtered by current user"""
        return AudioFile.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        """Save the audio file with the current user"""
        serializer.save(user=self.request.user)

    def calculate_speed_and_peaks(self, instance):
        """Calculate speed and peaks from audio file"""
        try:
            speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = calculate_speed_of_sound(
                float(instance.distance), instance.file.path, instance.unit
            )
            return speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted
        except Exception as e:
            logger.error(f"Error calculating speed and peaks: {str(e)}")
            return 0, "m/s", 0, "MPH", [], []

    def list(self, request, *args, **kwargs):
        """List audio files with speed calculations"""
        queryset = self.get_queryset()
        audio_files_data = []

        for instance in queryset:
            try:
                serializer = self.get_serializer(instance)
                speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = (
                    self.calculate_speed_and_peaks(instance)
                )
                audio_files_data.append(
                    {
                        **serializer.data,
                        "speed_mps": speed_mps,
                        "speed_unit": speed_unit,
                        "peaks": peaks,
                        "speed_mph": speed_mph,
                        "unit_mph": mph_unit,
                        "amplitude_formatted": amplitude_formatted,
                    }
                )
            except Exception as e:
                logger.error(f"Error processing audio file {instance.id}: {str(e)}")

        return Response(audio_files_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create new audio file entry"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = (
                    self.calculate_speed_and_peaks(serializer.instance)
                )

                return Response(
                    {
                        **serializer.data,
                        "speed_mps": speed_mps,
                        "speed_unit": speed_unit,
                        "peaks": peaks,
                        "speed_mph": speed_mph,
                        "unit_mph": mph_unit,
                        "amplitude_formatted": amplitude_formatted,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(f"Error in post: {str(e)}")
                return Response(
                    {"error": "Error processing audio file"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    lookup_field = "id"
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        """Get queryset filtered by current user"""
        return AudioFile.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Delete audio file and its data"""
        try:
            instance = self.get_object()
            instance.file.delete()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting audio file: {str(e)}")
            return Response(
                {"error": "Error deleting file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def calculate_speed_and_peaks(self, instance):
        """Calculate speed and peaks from audio file"""
        try:
            speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = calculate_speed_of_sound(
                float(instance.distance), instance.file.path, instance.unit
            )
            return speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted
        except Exception as e:
            logger.error(f"Error calculating speed and peaks: {str(e)}")
            return 0, "m/s", 0, "MPH", [], []

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single audio file with calculations"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = (
                self.calculate_speed_and_peaks(instance)
            )

            return Response(
                {
                    **serializer.data,
                    "speed_mps": speed_mps,
                    "speed_unit": speed_unit,
                    "peaks": peaks,
                    "speed_mph": speed_mph,
                    "unit_mph": mph_unit,
                    "amplitude_formatted": amplitude_formatted,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error retrieving audio file: {str(e)}")
            return Response(
                {"error": "Error retrieving file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, *args, **kwargs):
        """Partially update audio file"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = (
                    self.calculate_speed_and_peaks(instance)
                )
                return Response(
                    {
                        **serializer.data,
                        "speed_mps": speed_mps,
                        "speed_unit": speed_unit,
                        "peaks": peaks,
                        "speed_mph": speed_mph,
                        "unit_mph": mph_unit,
                        "amplitude_formatted": amplitude_formatted,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating audio file: {str(e)}")
            return Response(
                {"error": "Error updating file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, *args, **kwargs):
        """Fully update audio file"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)

            if serializer.is_valid():
                serializer.save()
                speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = (
                    self.calculate_speed_and_peaks(instance)
                )
                return Response(
                    {
                        **serializer.data,
                        "speed_mps": speed_mps,
                        "speed_unit": speed_unit,
                        "peaks": peaks,
                        "speed_mph": speed_mph,
                        "unit_mph": mph_unit,
                        "amplitude_formatted": amplitude_formatted,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating audio file: {str(e)}")
            return Response(
                {"error": "Error updating file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AudioStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        """Get statistics for all audio files of the current user"""
        try:
            audio_files = AudioFile.objects.filter(user=request.user).order_by(
                "-updated_at"
            )
            audio_statistics = []
            all_speeds = []

            for audio_file in audio_files:
                speed_mps, speed_unit, speed_mph, mph_unit, peaks, amplitude_formatted = calculate_speed_of_sound(
                    float(audio_file.distance),
                    audio_file.file.path,
                    audio_file.unit
                )

                if isinstance(speed_mph, (int, float)) and speed_mph > 0:
                    all_speeds.append(speed_mph)

                audio_statistics.append(
                    {
                        "file_name": audio_file.file.name,
                        "speed": speed_mph,
                        "speed_unit": mph_unit,
                        "peaks": peaks,
                        "distance": audio_file.distance,
                        "unit": audio_file.unit,
                        "amplitude_formatted": amplitude_formatted,
                    }
                )

            min_speed = min(all_speeds) if all_speeds else 0
            max_speed = max(all_speeds) if all_speeds else 0
            avg_speed = sum(all_speeds) / len(all_speeds) if all_speeds else 0

            response_data = {
                "audio_statistics": audio_statistics,
                "min_speed": round(min_speed, 2),
                "max_speed": round(max_speed, 2),
                "avg_speed": round(avg_speed, 2),
                "total_files": len(audio_files),
                "processed_files": len(all_speeds),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating audio statistics: {str(e)}")
            return Response(
                {"error": "Error generating statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )