from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from core.models import AudioFile
from unittest.mock import patch
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup
User = get_user_model()


class AudioFileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser",
            name="Test User",
            password="password123",
            phone_number="03459100704",
        )
        self.client.force_authenticate(user=self.user)
        self.audio_file_url = reverse("audiofile-list-create")
        self.distance = 10.0

    def create_test_audio_file(self):
        audio_data = BytesIO(b"Dummy audio data")
        audio_file = SimpleUploadedFile(
            "test_audio.wav", audio_data.read(), content_type="audio/wav"
        )
        return audio_file

    # Write Tests for CRUD Operations
    @patch("app.utils.calculate_speed_of_sound", return_value=(343.0, [100, 200]))
    def test_create_audio_file(self, mock_calculate_speed):
        audio_file = self.create_test_audio_file()
        response = self.client.post(
            self.audio_file_url, {"file": audio_file, "distance": self.distance}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("speed", response.data)
        self.assertEqual(response.data["speed"], 343.0)
        self.assertIn("peaks", response.data)
        self.assertEqual(response.data["peaks"], [100, 200])

    def test_list_audio_files(self):
        AudioFile.objects.create(
            user=self.user, file=self.create_test_audio_file(), distance=self.distance
        )
        response = self.client.get(self.audio_file_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(
            len(response.data["results"]), 1
        )  # Check at least one result

    def test_retrieve_audio_file(self):
        audio_file_instance = AudioFile.objects.create(
            user=self.user, file=self.create_test_audio_file(), distance=self.distance
        )
        url = reverse("audiofile-detail", args=[audio_file_instance.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], audio_file_instance.id)

    def test_delete_audio_file(self):
        audio_file_instance = AudioFile.objects.create(
            user=self.user, file=self.create_test_audio_file(), distance=self.distance
        )
        url = reverse("audiofile-detail", args=[audio_file_instance.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AudioFile.objects.filter(id=audio_file_instance.id).exists())

    def test_update_audio_file(self):
        audio_file_instance = AudioFile.objects.create(
            user=self.user, file=self.create_test_audio_file(), distance=self.distance
        )
        new_distance = 15.0
        url = reverse("audiofile-detail", args=[audio_file_instance.id])
        response = self.client.patch(url, {"distance": new_distance}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        audio_file_instance.refresh_from_db()
        self.assertEqual(audio_file_instance.distance, new_distance)

    # Run Tests for Edge Cases
    def test_create_audio_file_without_distance(self):
        audio_file = self.create_test_audio_file()
        response = self.client.post(self.audio_file_url, {"file": audio_file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "distance", response.data
        )  # Check that distance field is required

    def test_retrieve_nonexistent_audio_file(self):
        url = reverse(
            "audiofile-detail", args=[9999]
        )  # Assuming ID 9999 does not exist
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_audio_file(self):
        url = reverse(
            "audiofile-detail", args=[9999]
        )  # Assuming ID 9999 does not exist
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
