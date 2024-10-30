"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from ..models import AudioFile


def create_user(email="user@example.com", password="testPass123", **extra_fields):
    """Create a sample user"""
    if len(password) < 8:
        raise ValueError("Password is too short")
    return get_user_model().objects.create_user(email, password, **extra_fields)


class ModelTests(TestCase):
    """Test Models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with required fields is successful"""
        user = create_user(
            email="test@example.com",
            name="Haris ahmad",
            password="testpass123",
            phone_number="03459100704",
        )

        self.assertEqual(user.name, "Haris ahmad")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.phone_number, "03459100704")
        self.assertTrue(user.check_password("testpass123"))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["test2@Example.com", "test2@example.com"],
            ["test3@example.COM", "test3@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_user_with_all_fields_successful(self):
        """Test creating a user with all fields is successful"""
        email = "full@example.com"
        password = "testPass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name="Test User",
            phone_number="1234567890",
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.phone_number, "1234567890")

    def test_user_image_field(self):
        """Test creating a user with an image"""
        email = "imageuser@example.com"
        user = get_user_model().objects.create_user(
            email=email,
            password="testPass123",
            image="path/to/image.jpg",
        )

        self.assertEqual(user.image, "path/to/image.jpg")

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_user_with_invalid_phone_number_raises_error(self):
        """Test that creating a user with an invalid phone number raises a ValidationError"""
        with self.assertRaises(ValidationError):

            user = create_user(
                email="invalidphone@example.com",
                password="testPass123",
                phone_number="12345678901234",
            )

            user.full_clean()  # Ensure validation occurs before save

    def test_inactive_user_creation(self):
        """Test creating an inactive user"""
        user = create_user(
            email="inactive@example.com",
            password="testPass123",
            is_active=False,
        )
        self.assertFalse(user.is_active)


class AudioFileModelTests(TestCase):
    """Test AudioFile Model."""

    def setUp(self):
        self.user = create_user(
            email="inactive@example.com",
            password="testPass123",
            name="Test User",
            phone_number="03459100704",
        )

    def test_create_audio_file_successful(self):
        """Test creating an AudioFile instance is successful."""
        audio_file = AudioFile.objects.create(
            user=self.user,
            file="path/to/audio.mp3",
            distance=5.0,
        )
        self.assertEqual(audio_file.user, self.user)
        self.assertEqual(audio_file.distance, 5.0)
        self.assertEqual(
            str(audio_file), f"Audio File {audio_file.id} for user {self.user.email}"
        )

    def test_audio_file_creation_without_user_raises_error(self):
        """Test creating an AudioFile without a user raises an error."""
        audio_file = AudioFile(
            user=None,
            file="path/to/audio.mp3",
            distance=5.0,
        )
        with self.assertRaises(ValueError):
            audio_file.clean()
            audio_file.save()

    def test_negative_distance_raises_validation_error(self):
        """Test creating an AudioFile with negative distance raises ValidationError."""
        audio_file = AudioFile(user=self.user, file="path/to/audio.mp3", distance=-1.0)
        with self.assertRaises(ValidationError):
            audio_file.clean()  # Explicitly call clean method for validation
            audio_file.save()  # This should not be reached due to the validation error

    def test_audio_file_auto_update(self):
        """Test updated_at field is automatically updated."""
        audio_file = AudioFile.objects.create(
            user=self.user,
            file="path/to/audio.mp3",
            distance=5.0,
        )
        original_updated_at = audio_file.updated_at
        audio_file.distance = 10.0
        audio_file.save()
        self.assertNotEqual(original_updated_at, audio_file.updated_at)
