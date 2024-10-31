from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from core.models import AudioFile
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# Define URLs using their names
AUDIO_FILE_URL = reverse("audio:audiofile-list-create")


class AudioFileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="password123",
            phone_number="03459100704",
        )
        self.client.force_authenticate(user=self.user)
        self.distance = 60.0

    def create_test_audio_file(self):
        """Create a dummy audio file for testing."""
        audio_data = BytesIO(b"Dummy audio data")
        return SimpleUploadedFile(
            "test_audio.wav", audio_data.read(), content_type="audio/wav"
        )

    def test_create_audio_file_success(self):
        """Test creating an audio file is successful."""
        payload = {
            "file": self.create_test_audio_file(),
            "distance": 64.0,
        }
        res = self.client.post(AUDIO_FILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AudioFile.objects.count(), 1)
        self.assertEqual(AudioFile.objects.get().user, self.user)

    def test_audio_file_detail_url(self):
        """Test retrieving an audio file detail URL works."""
        audio_file = AudioFile.objects.create(
            user=self.user, file=self.create_test_audio_file(), distance=self.distance
        )
        detail_url = reverse("audio:audiofile-detail", args=[audio_file.id])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], audio_file.id)

    def test_create_audio_file_invalid(self):
        """Test creating an audio file fails with invalid data."""
        payload = {
            "distance": 10.0,
        }
        res = self.client.post(AUDIO_FILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AudioFile.objects.count(), 0)

    def test_create_audio_file_unauthenticated(self):
        """Test creating an audio file fails when unauthenticated."""
        self.client.logout()
        payload = {
            "file": self.create_test_audio_file(),
            "distance": 10.0,
        }
        res = self.client.post(AUDIO_FILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_audio_file_list(self):
        """Test retrieving the list of audio files."""
        self.client.post(
            AUDIO_FILE_URL,
            {
                "file": self.create_test_audio_file(),
                "distance": 10.0,
            },
        )
        self.client.post(
            AUDIO_FILE_URL,
            {
                "file": self.create_test_audio_file(),
                "distance": 15.0,
            },
        )

        res = self.client.get(AUDIO_FILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_audio_file_detail(self):
        """Test retrieving a single audio file detail."""
        audio_file_response = self.client.post(
            AUDIO_FILE_URL,
            {
                "file": self.create_test_audio_file(),
                "distance": 10.0,
            },
        )

        # Get the id from the response data
        audio_file_id = audio_file_response.data["id"]
        detail_url = reverse("audio:audiofile-detail", args=[audio_file_id])
        res = self.client.get(detail_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], audio_file_id)

    def test_delete_audio_file(self):
        """Test deleting an audio file."""
        audio_file_response = self.client.post(
            AUDIO_FILE_URL,
            {
                "file": self.create_test_audio_file(),
                "distance": 10.0,
            },
        )

        # Get the id from the response data
        audio_file_id = audio_file_response.data["id"]
        detail_url = reverse("audio:audiofile-detail", args=[audio_file_id])
        res = self.client.delete(detail_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AudioFile.objects.count(), 0)
