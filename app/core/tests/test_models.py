"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


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
