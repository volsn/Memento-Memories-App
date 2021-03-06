from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@mail.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email"""
        email = 'test@email.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@EMAIL.COM'
        user = get_user_model().objects.create_user(
            email=email,
            password='test123'
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raise error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@email.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Spot ideas'
        )
        self.assertEqual(str(tag), tag.name)

    def test_domain_str(self):
        """Test the domain test representation"""
        domain = models.Domain.objects.create(
            user=sample_user(),
            name='Friendship'
        )

        self.assertEqual(str(domain), domain.name)

    def test_memory_str(self):
        memory = models.Memory.objects.create(
            user=sample_user(),
            title='Call Sam'
        )

        self.assertEqual(str(memory), memory.title)

    @patch('uuid.uuid4')
    def test_memory_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.image_upload_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/memories/{uuid}.jpg'
        self.assertRegex(file_path, exp_path)
