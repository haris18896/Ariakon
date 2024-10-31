from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, generics, authentication, permissions


from core.models import AudioFile
from .serializers import AudioFileSerializer
from .utils import calculate_speed_of_sound


class AudioFileListView(generics.ListCreateAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    pagination_class = LimitOffsetPagination
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return AudioFile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        distance = request.data.get("distance", 0)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            audio_file_path = serializer.instance.file.path
            # speed, peaks = calculate_speed_of_sound(float(distance), audio_file_path)
            return Response(
                {**serializer.data}, status=status.HTTP_201_CREATED
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

    def calculate_and_respond(self, instance, serializer_data):
        """Helper function to calculate speed and peaks and format the response."""
        distance = getattr(instance, "distance", 0)
        print("distance : ", distance)
        audio_file_path = instance.file.path
        print("audio_file_path: ", audio_file_path)
        # speed, peaks = calculate_speed_of_sound(float(distance), audio_file_path)
        return Response({**serializer_data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # return Response({**serializer.data}, status=status.HTTP_200_OK)
        return self.calculate_and_respond(instance, serializer.data)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return self.calculate_and_respond(instance, serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return self.calculate_and_respond(instance, serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
